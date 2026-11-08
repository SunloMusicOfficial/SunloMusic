# Copyright (C) @itsSmartDev

import asyncio
from typing import Optional, Tuple
from pyrogram import Client, types
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    UserAlreadyParticipant, InviteHashExpired, UsersTooMuch,
    FloodWait, ChatAdminRequired, UserBannedInChannel
)
from SunloMusic.core.logging import logger

Result = Tuple[bool, Optional[str]]

BAN_KEYWORDS = ('banned', 'ban', 'user_banned', 'kicked', 'channel_private', 'username not found')
PENDING_KEYWORDS = ('invite_request_sent', 'request_sent', 'user_not_participant', 'join request',
                    "not a member of this chat")

BANNED_TITLE = "Assistant Account Banned"
PENDING_TITLE = "Join Request Pending"


class JoinNotice(str):
    """Plain-text (markdown) notice that can also carry a rich message version of itself."""

    rich_message: Optional[types.InputRichMessage] = None
    reply_markup: Optional[types.InlineKeyboardMarkup] = None

    def __new__(cls, text: str, rich_message: Optional[types.InputRichMessage] = None,
                reply_markup: Optional[types.InlineKeyboardMarkup] = None):
        obj = super().__new__(cls, text)
        obj.rich_message = rich_message
        obj.reply_markup = reply_markup
        return obj


class AutoJoinHandler:

    @staticmethod
    def is_blocking_error(join_error: Optional[str]) -> bool:
        """True when retrying with the next queued track cannot help until a human acts."""
        if not join_error:
            return False
        return BANNED_TITLE in join_error or PENDING_TITLE in join_error or "banned" in join_error.lower()

    @staticmethod
    def _is_pending_error(error: Exception) -> bool:
        text = str(error).lower()
        return any(keyword in text for keyword in PENDING_KEYWORDS)

    @staticmethod
    def _is_ban_error(error: Exception) -> bool:
        text = str(error).lower()
        return any(keyword in text for keyword in BAN_KEYWORDS)

    @staticmethod
    async def _assistant_identity(user_client: Client):
        me = getattr(user_client, 'me', None)
        if not me:
            me = await user_client.get_me()
        return me

    @staticmethod
    async def _assistant_label(user_client: Client) -> str:
        try:
            me = await AutoJoinHandler._assistant_identity(user_client)
            return f"@{me.username}" if me.username else (me.first_name or str(me.id))
        except Exception:
            return "the assistant account"

    @staticmethod
    async def _banned_message(user_client: Client) -> str:
        label = await AutoJoinHandler._assistant_label(user_client)
        return (
            f"❌ **{BANNED_TITLE}**\n\n"
            f"Assistant account ({label}) is currently banned in this group.\n\n"
            f"Please unban {label} manually and then try again."
        )

    @staticmethod
    async def _pending_message(user_client: Client, chat_id: int) -> JoinNotice:
        label = await AutoJoinHandler._assistant_label(user_client)

        def who(bold: bool):
            # Telegram turns "@username" in rich text into a mention by itself; explicit mention objects are rejected.
            return types.RichTextBold(label) if bold else label

        def step(*parts):
            return types.InputRichBlockListItem(blocks=[types.InputRichBlockParagraph(list(parts))], type="1")

        rich = types.InputRichMessage(blocks=[
            types.InputRichBlockSectionHeading(f"⏳ {PENDING_TITLE}", size=1),
            types.InputRichBlockDivider(),
            types.InputRichBlockParagraph([
                "Assistant ", who(bold=True), " needs admin approval to join this group and play music.",
            ]),
            types.InputRichBlockSectionHeading("Action Required", size=2),
            types.InputRichBlockList([
                step("Open the ", types.RichTextBold("Join Requests"), " list."),
                step(types.RichTextBold("Approve"), " ", who(bold=False), "."),
                step("Send the ", types.RichTextBold("play"), " command again."),
            ]),
            types.InputRichBlockBlockQuotation([
                types.InputRichBlockParagraph([
                    "💡 ", types.RichTextBold("Tip:"), " Make the bot Admin with ",
                    types.RichTextBold("Invite Users"), " permission to auto-approve requests.",
                ]),
            ]),
        ])

        text = (
            f"⏳ **{PENDING_TITLE}**\n\n"
            f"Assistant **{label}** needs admin approval to join this group and play music.\n\n"
            f"**Action Required**\n"
            f"1. Open the **Join Requests** list.\n"
            f"2. **Approve** {label}.\n"
            f"3. Send the **play** command again.\n\n"
            f"💡 **Tip:** Make the bot Admin with **Invite Users** permission to auto-approve requests."
        )
        from SunloMusic.ui.keyboards import keyboards
        return JoinNotice(text, rich, keyboards.close_only(chat_id))

    @staticmethod
    async def ensure_user_in_chat(bot_client: Client, user_client: Client, chat_id: int) -> Result:
        try:
            banned = False
            try:
                member = await user_client.get_chat_member(chat_id, "me")
                if member.status == ChatMemberStatus.BANNED:
                    banned = True
                elif member.status != ChatMemberStatus.LEFT:
                    logger.info(f"User client is already in chat {chat_id}")
                    return True, None
            except UserBannedInChannel:
                banned = True
            except Exception as e:
                if AutoJoinHandler._is_ban_error(e):
                    logger.warning(f"User client appears to be banned in {chat_id} (error: {e})")
                    banned = True

            if banned:
                logger.warning(f"User client is banned in {chat_id}, attempting to unban...")
                success, msg = await AutoJoinHandler._handle_banned_user(bot_client, user_client, chat_id)
                if not success:
                    return False, msg

            logger.info(f"User client not in chat {chat_id}, starting auto-join process")
            chat = await bot_client.get_chat(chat_id)

            if chat.username:
                return await AutoJoinHandler._join_public_group(bot_client, user_client, chat.username, chat_id)
            return await AutoJoinHandler._join_private_group(bot_client, user_client, chat_id)

        except ChatAdminRequired:
            error_msg = "❌ **Bot needs admin permission**\n\nThe bot must be an admin with the following permissions:\n• Invite users\n• Export invite links\n• Manage voice chats"
            logger.error(f"Bot lacks admin permissions in {chat_id}")
            return False, error_msg

        except Exception as e:
            if AutoJoinHandler._is_pending_error(e):
                logger.info(f"Assistant join for {chat_id} is waiting on a join request ({e})")
                return False, await AutoJoinHandler._pending_message(user_client, chat_id)
            error_msg = f"❌ **Failed to add user client to group**\n\nError: {str(e)}"
            logger.error(f"Unexpected error in auto-join for {chat_id}: {e}")
            return False, error_msg

    @staticmethod
    async def _confirm_membership(user_client: Client, chat_id: int) -> str:
        """Returns 'member', 'banned' or 'pending' (not a participant yet)."""
        try:
            member = await user_client.get_chat_member(chat_id, "me")
        except UserBannedInChannel:
            return 'banned'
        except Exception as e:
            if AutoJoinHandler._is_pending_error(e):
                return 'pending'
            if AutoJoinHandler._is_ban_error(e):
                return 'banned'
            raise
        if member.status == ChatMemberStatus.BANNED:
            return 'banned'
        if member.status == ChatMemberStatus.LEFT:
            return 'pending'
        return 'member'

    @staticmethod
    async def _handle_pending_request(bot_client: Client, user_client: Client, chat_id: int) -> Result:
        """The join was sent as a request: try to approve it as the bot, otherwise tell the admins what to do."""
        try:
            me = await AutoJoinHandler._assistant_identity(user_client)
            logger.info(f"Join request pending for assistant {me.id} in {chat_id}, trying to approve as bot")
            await bot_client.approve_chat_join_request(chat_id, me.id)
            logger.info(f"Approved join request for assistant {me.id} in {chat_id}")
        except Exception as approve_error:
            logger.warning(f"Bot could not approve the assistant's join request in {chat_id}: {approve_error}")
            return False, await AutoJoinHandler._pending_message(user_client, chat_id)

        for _ in range(3):
            await asyncio.sleep(2)
            try:
                if await AutoJoinHandler._confirm_membership(user_client, chat_id) == 'member':
                    logger.info(f"Assistant confirmed as member of {chat_id} after approval")
                    return True, None
            except Exception as check_error:
                logger.debug(f"Membership re-check failed in {chat_id}: {check_error}")
        return False, await AutoJoinHandler._pending_message(user_client, chat_id)

    @staticmethod
    async def _invite_link(bot_client: Client, chat_id: int, fresh: bool = False) -> Tuple[Optional[str], Optional[str]]:
        if not fresh:
            try:
                chat = await bot_client.get_chat(chat_id)
                if getattr(chat, 'invite_link', None):
                    logger.info(f"Using existing invite link for {chat_id}")
                    return chat.invite_link, None
            except Exception:
                pass
        try:
            logger.info(f"Exporting new invite link for {chat_id}")
            return await bot_client.export_chat_invite_link(chat_id), None
        except ChatAdminRequired:
            logger.error(f"Bot lacks permission to export invite link in {chat_id}")
            return None, "❌ **Bot needs admin permission**\n\nThe bot must be an admin to invite the assistant account."
        except Exception as e:
            logger.error(f"Failed to export invite link for {chat_id}: {e}")
            return None, f"❌ **Failed to create invite link**\n\nError: {str(e)}"

    @staticmethod
    async def _join(bot_client: Client, user_client: Client, chat_id: int, username: Optional[str], allow_unban: bool = True) -> Result:
        if username:
            target = username
        else:
            target, link_error = await AutoJoinHandler._invite_link(bot_client, chat_id, fresh=not allow_unban)
            if not target:
                return False, link_error

        banned = pending = False
        try:
            logger.info(f"Assistant joining {chat_id} via {'@' + username if username else 'invite link'}")
            await user_client.join_chat(target)
        except UserAlreadyParticipant:
            logger.info(f"Assistant already in {chat_id}")
            return True, None
        except FloodWait as e:
            logger.warning(f"FloodWait {e.value}s when joining {chat_id}")
            return False, f"❌ **Rate limited**\n\nPlease wait {e.value} seconds and try again."
        except UsersTooMuch:
            logger.error(f"Group {chat_id} is full")
            return False, "❌ **Group is full**\n\nThe group has reached its member limit."
        except (UserBannedInChannel, InviteHashExpired):
            banned = True
        except Exception as e:
            if AutoJoinHandler._is_pending_error(e):
                pending = True
            elif AutoJoinHandler._is_ban_error(e):
                banned = True
            else:
                raise

        if not banned and not pending:
            await asyncio.sleep(1.5)
            state = await AutoJoinHandler._confirm_membership(user_client, chat_id)
            if state == 'member':
                logger.info(f"Assistant confirmed as member of {chat_id}")
                return True, None
            banned, pending = state == 'banned', state == 'pending'

        if pending:
            return await AutoJoinHandler._handle_pending_request(bot_client, user_client, chat_id)

        logger.warning(f"Assistant appears to be banned in {chat_id}")
        if not allow_unban:
            return False, await AutoJoinHandler._banned_message(user_client)
        success, msg = await AutoJoinHandler._handle_banned_user(bot_client, user_client, chat_id)
        if not success:
            return False, msg
        return await AutoJoinHandler._join(bot_client, user_client, chat_id, username, allow_unban=False)

    @staticmethod
    async def _join_public_group(bot_client: Client, user_client: Client, username: str, chat_id: int) -> Result:
        try:
            return await AutoJoinHandler._join(bot_client, user_client, chat_id, username)
        except ChatAdminRequired:
            raise
        except Exception as e:
            if AutoJoinHandler._is_pending_error(e):
                return False, await AutoJoinHandler._pending_message(user_client, chat_id)
            logger.error(f"Failed to join public group @{username}: {e}")
            return False, f"❌ **Failed to join public group**\n\nError: {str(e)}"

    @staticmethod
    async def _join_private_group(bot_client: Client, user_client: Client, chat_id: int) -> Result:
        temp_message = None
        try:
            temp_message = await bot_client.send_message(
                chat_id,
                "🔄 **Adding assistant to group...**\n\nPlease wait a moment."
            )
            result = await AutoJoinHandler._join(bot_client, user_client, chat_id, None)
            if result[0]:
                try:
                    await user_client.resolve_peer(chat_id)
                    logger.info(f"Resolved peer for {chat_id} to refresh session")
                except Exception:
                    pass
            return result
        except ChatAdminRequired:
            raise
        except Exception as e:
            if AutoJoinHandler._is_pending_error(e):
                return False, await AutoJoinHandler._pending_message(user_client, chat_id)
            logger.error(f"Failed to join private group {chat_id}: {e}")
            return False, f"❌ **Failed to join private group**\n\nError: {str(e)}"
        finally:
            if temp_message:
                try:
                    await temp_message.delete()
                except Exception:
                    pass

    @staticmethod
    async def _handle_banned_user(bot_client: Client, user_client: Client, chat_id: int) -> Result:
        user_id = None
        try:
            user_id = (await AutoJoinHandler._assistant_identity(user_client)).id

            logger.info(f"Attempting to unban user {user_id} in {chat_id}")

            await bot_client.unban_chat_member(chat_id, user_id)
            logger.info(f"Successfully unbanned user {user_id} in {chat_id}")

            await asyncio.sleep(2)

            return True, None

        except ChatAdminRequired:
            logger.error(f"Bot lacks permission to unban user in {chat_id}")
            return False, await AutoJoinHandler._banned_message(user_client)

        except Exception as e:
            error_str = str(e).lower()

            if 'not found' in error_str or 'not a member' in error_str:
                logger.info(f"User {user_id} is not banned in {chat_id}, just not a member")
                return True, None

            logger.error(f"Failed to unban user in {chat_id}: {e}")
            return False, await AutoJoinHandler._banned_message(user_client)

auto_join_handler = AutoJoinHandler()

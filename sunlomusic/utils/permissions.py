# Copyright (C) @YO_UR_OFFICIAL_CRUSH

from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from pyrogram.raw import functions, types
from sunlomusic.core.logging import logger
from sunlomusic.db import db

class PermissionChecker:
    @staticmethod
    async def is_admin(client: Client, chat_id: int, user_id: int) -> bool:
        try:
            member = await client.get_chat_member(chat_id, user_id)
            return member.status in [
                ChatMemberStatus.OWNER,
                ChatMemberStatus.ADMINISTRATOR
            ]
        except Exception as e:
            logger.error(f"Failed to check admin status: {e}")
            return False

    @staticmethod
    async def check_admin(client: Client, message: Message, require_admin: bool = False) -> bool:
        if not message.from_user:
            return False

        user_id = message.from_user.id
        chat_id = message.chat.id

        is_group_admin = await PermissionChecker.is_admin(client, chat_id, user_id)
        is_vc_admin = await db.is_vc_admin(chat_id, user_id)

        if is_group_admin or is_vc_admin:
            return True

        if require_admin:
            await message.reply_text("❌ Only group admins can perform this action.")
            return False

        settings = await db.get_chat_settings(chat_id)
        admin_only = settings.get('admin_only', False)

        if not admin_only:
            return True

        await message.reply_text("❌ Only group admins can perform this action.")
        return False

    @staticmethod
    async def can_use_playlist(client: Client, message: Message) -> bool:
        if not message.from_user:
            return False

        user_id = message.from_user.id
        chat_id = message.chat.id

        is_group_admin = await PermissionChecker.is_admin(client, chat_id, user_id)
        is_vc_admin = await db.is_vc_admin(chat_id, user_id)

        if is_group_admin or is_vc_admin:
            return True

        settings = await db.get_chat_settings(chat_id)
        playlist_permission = settings.get('playlist_permission', 'everyone')

        if playlist_permission == 'everyone':
            return True

        await message.reply_text("❌ Only group admins can load playlists.")
        return False

    @staticmethod
    async def can_edit_group_call_title(user_client: Client, chat_id: int) -> tuple[bool, str]:
        try:
            me = await user_client.get_me()
            user_id = me.id

            member = await user_client.get_chat_member(chat_id, user_id)

            if member.status == ChatMemberStatus.OWNER:
                logger.info(f"User client is owner in {chat_id}, has permission to edit group call title")
                return True, ""

            if member.status == ChatMemberStatus.ADMINISTRATOR:
                if not member.privileges:
                    logger.warning(f"User client admin privileges are None in {chat_id}")
                    return False, "User client is admin but missing 'Manage Voice Chats' permission. Please enable this permission in admin settings."

                can_manage_video = getattr(member.privileges, 'can_manage_video_chats', None)
                can_manage_voice = getattr(member.privileges, 'can_manage_voice_chats', None)

                logger.info(f"Privileges check for {chat_id}: can_manage_video_chats={can_manage_video}, can_manage_voice_chats={can_manage_voice}")

                if can_manage_video or can_manage_voice:
                    logger.info(f"User client has 'Manage Voice Chats' permission in {chat_id}")
                    return True, ""
                else:
                    return False, "User client is admin but missing 'Manage Voice Chats' permission. Please enable this permission in admin settings."

            return False, "User client is not an admin in this chat. Please make the user account admin with 'Manage Voice Chats' permission."

        except Exception as e:
            logger.error(f"Error checking group call title permission: {e}")
            return False, f"Failed to check permission: {str(e)}"

permission_checker = PermissionChecker()

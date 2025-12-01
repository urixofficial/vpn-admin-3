from core.config import settings
from core.logger import log
from core.repos.message import message_repo
from core.repos.user import user_repo
from core.schemas.message import CreateMessage
from core.schemas.user import ReadUser, UpdateUser


async def debiting_funds():
	log.debug("Запуск списания средств")
	users: list[ReadUser] = await user_repo.get_active()
	print(users)
	daily_payment = settings.billing.daily_payment
	counter = 0
	for user in users:
		if user.balance < daily_payment:
			# await user_repo.update(user.id, UpdateUser(is_active=False))
			await user_repo.block(user.id)
			log.info("Учетная запись {} ({}) заблокирована".format(user.name, user.id))
			text = "Ваша учетная запись заблокирована! Для возобновления сервиса внесите оплату."
			notification = CreateMessage(chat_id=user.id, text=text)
			await message_repo.send_message(notification)
			counter += 1
		else:
			new_balance = user.balance - daily_payment
			updated_user = await user_repo.update(user.id, UpdateUser(balance=new_balance))
			if updated_user.balance < daily_payment:
				text = "На вашем счете недостаточно средств! Пожалуйста внесите оплату."
				notification = CreateMessage(chat_id=updated_user.id, text=text)
				await message_repo.send_message(notification)
				counter += 1
	log.debug("Списание средств завершено. Отправлено уведомлений: {}".format(counter))

from aiogram.fsm.state import StatesGroup, State


class TransactionCrudStates(StatesGroup):
	create_enter_user_id = State()
	create_enter_amount = State()
	show_enter_id = State()
	show_profile = State()
	update = State()
	delete_confirmation = State()


class AdminPaymentStates(StatesGroup):
	confirmation = State()

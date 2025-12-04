from aiogram.fsm.state import StatesGroup, State


class UserCrudStates(StatesGroup):
	create_enter_id = State()
	create_enter_name = State()
	show_enter_id = State()
	show_profile = State()
	update_user = State()
	delete_confirmation = State()


class AdminRegistrationStates(StatesGroup):
	confirmation = State()

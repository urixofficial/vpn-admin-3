from aiogram.fsm.state import StatesGroup, State


class AwgCrudStates(StatesGroup):
	show_enter_id = State()
	show_profile = State()
	delete_confirmation = State()

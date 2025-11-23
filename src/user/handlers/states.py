from aiogram.fsm.state import StatesGroup, State

class CrudUserStates(StatesGroup):
	create_enter_id = State()
	create_enter_name = State()
	show_enter_id = State()
	show_profile = State()
	delete_confirmation = State()

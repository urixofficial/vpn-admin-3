import subprocess
from ipaddress import ip_network

from core.config import AwgSettings
from core.logger import log
from core.schemas.awg import ReadAwgRecord


def save_file(data: str, path: str) -> bool:
	log.debug("Сохранение файла: {}".format(path))
	try:
		with open(path, "w") as f:
			f.write(data)
		log.debug("Файл успешно сохранен: {}".format(path))
		return True
	except Exception as e:
		log.error("Ошибка при сохранении файла {}: {}".format(path, e))
		return False


def restart_interface(interface: str) -> bool:
	log.debug("Перезапуск интерфейса {}".format(interface))
	try:
		subprocess.run(
			["sudo", "awg-quick", "down", interface],
			check=True,
			capture_output=True,
			text=True,
		)
		subprocess.run(
			["sudo", "awg-quick", "up", interface],
			check=True,
			capture_output=True,
			text=True,
		)
		log.info("OK")
		return True
	except Exception as e:
		log.error("Ошибка перезапуска интерфейса {}: {}".format(interface, e))
		return False


def generate_key_pair() -> tuple[str, str]:
	log.debug("Генерация пары ключей AWG")
	try:
		private_key = subprocess.run(
			["sudo", "awg", "genkey"],
			capture_output=True,
			text=True,
			check=True,
		).stdout.strip()
		public_key = subprocess.run(
			["sudo", "awg", "pubkey"],
			input=private_key,
			capture_output=True,
			text=True,
			check=True,
		).stdout.strip()
		log.debug("Ключи успешно сгенерированы")
		return private_key, public_key
	except Exception as e:
		log.error("Ошибка генерации ключей: {}".format(e))
		raise


def get_free_ip(awg_records: list[ReadAwgRecord], subnet: str, mask: int) -> str | None:
	log.debug("Поиск свободного IP-адреса")
	subnet = ip_network(f"{subnet}/{mask}")
	used_ips = {awg_record.ip for awg_record in awg_records}
	for ip in subnet.hosts():
		if ip == subnet.network_address + 1:
			continue
		ip_str = str(ip)
		if ip_str not in used_ips:
			log.debug("Найден свободный IP: {}".format(ip_str))
			return ip_str
	log.warning("Свободные IP-адреса не найдены")
	return None


def create_user_config(awg_record: ReadAwgRecord, awg_config: AwgSettings) -> str:
	log.debug("Создание конфигурации AWG для пользователя")
	user_config = (
		f"[Interface]\n"
		f"PrivateKey = {awg_record.private_key}\n"
		f"Address = {awg_record.ip}/{awg_record.mask}\n"
		f"DNS = {awg_config.dns}\n"
		f"Jc = {awg_config.jc}\n"
		f"Jmin = {awg_config.jmin}\n"
		f"Jmax = {awg_config.jmax}\n"
		f"S1 = {awg_config.s1}\n"
		f"S2 = {awg_config.s2}\n"
		f"H1 = {awg_config.h1}\n"
		f"H2 = {awg_config.h2}\n"
		f"H3 = {awg_config.h3}\n"
		f"H4 = {awg_config.h4}\n\n"
		f"[Peer]\n"
		f"PublicKey = {awg_config.server_public_key}\n"
		f"AllowedIPs = 0.0.0.0/0, ::/0\n"
		f"Endpoint = {awg_config.server_ip}:{awg_config.server_port}\n"
		f"PersistentKeepalive = 25\n"
	)
	return user_config


def create_server_interface_config(awg_config: AwgSettings) -> str:
	log.debug("Создание секции Interface конфигурации AWG для сервера")
	interface_section = (
		f"[Interface]\n"
		f"ListenPort = {awg_config.server_port}\n"
		f"PrivateKey = {awg_config.server_private_key}\n"
		f"Jc = {awg_config.jc}\n"
		f"Jmin = {awg_config.jmin}\n"
		f"Jmax = {awg_config.jmax}\n"
		f"S1 = {awg_config.s1}\n"
		f"S2 = {awg_config.s2}\n"
		f"H1 = {awg_config.h1}\n"
		f"H2 = {awg_config.h2}\n"
		f"H3 = {awg_config.h3}\n"
		f"H4 = {awg_config.h4}\n\n"
	)
	return interface_section


def create_server_peers_config(awg_records: list[ReadAwgRecord]) -> str:
	log.debug("Создание секции Peers конфигурации AWG для сервера")
	peers_section = ""
	for awg_record in awg_records:
		peer_section = (
			f"[Peer]\nPublicKey = {awg_record.public_key}\nAllowedIPs = {awg_record.ip}/{awg_record.mask}\n\n"
		)
		peers_section += peer_section
	return peers_section


def sync_server_config(interface: str, config_path: str):
	log.debug("Синхронизация интерфейса {} с конфигурации: {}".format(interface, config_path))
	try:
		subprocess.run(
			["sudo", "awg", "syncconf", interface, config_path],
			check=True,
			capture_output=True,
			text=True,
		)
		log.info("OK")
		return True

	except Exception as e:
		log.error("Ошибка синхронизации конфигурации сервера: {}".format(e))
		return False

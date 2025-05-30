# SPDX-License-Identifier: Apache-2.0
# Copyright 2015-2022 Espressif Systems (Shanghai) PTE LTD
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from py_parse.process import *


class ctrl_cmd(object):
	def __init__(self):
		self.out = ""

	def __str__(self):
		return self.out


	def wifi_get_mode(self):
		"""Get Wi-Fi mode

		Args:
			no_arg(str,optional): O | Dummy arg

		Returns:
			ctrl_cmd: ctrl_cmd object
		"""

		self.out = process_get_mode()
		return self


	def wifi_set_mode(self, mode : str):
		"""Set Wi-Fi mode

		Args:
			mode(str, mandatory): M | Values: ['station' | 'softap' | 'station+softap']

		Returns:
			ctrl_cmd: ctrl_cmd object
		"""
		if process_is_param_missing(mode):
			self.out = "Missing param " + "--mode"
			return self

		self.out = process_set_mode(mode)
		return self


	def wifi_get_mac(self, mode : str):
		"""Get MAC address for mode passed

		Args:
			mode(int, mandatory): M | Values: ['station' | 'softap']

		Returns:
			ctrl_cmd: ctrl_cmd object
		"""

		self.out = process_get_mac_addr(mode)
		return self


	def wifi_set_mac(self, mode : str = "", mac : str = ""):
		"""Set MAC address for mode passed

		Args:
			mode(str, mandatory): M | Values: ['station' | 'softap']
			mac(str, mandatory): M | Mac address

		Returns:
			ctrl_cmd: ctrl_cmd object
		"""

		if process_is_param_missing(mode):
			self.out = "Missing param " + "--mode"
			return self
		if process_is_param_missing(mac):
			self.out = "Missing param " + "--mac"
			return self

		self.out = process_set_mac_addr(mode, mac)
		return self


	def get_available_ap(self):
		"""Get neighboring AP (Wi-Fi routers or hotspots)

		Args:
			no_arg(str,optional): O | Dummy arg

		Returns:
			ctrl_cmd: ctrl_cmd object
		"""
		self.out = process_get_available_wifi()
		return self


	def connect_ap(self, ssid : str = "", pwd : str = "", bssid : str = "", use_wpa3 : bool = False, listen_interval : int = 3, band_mode: int = WIFI_BAND_MODE_AUTO):
		"""Connect to AP (Wi-Fi router or hotspot)

		Args:
			ssid (str, mandatory): M | SSID of AP (Wi-Fi router)
			pwd(str, optional): O | Password of AP (Wi-Fi router) to connect to
			bssid(str, optional): O | MAC addr of AP (useful when multiple AP have same SSID) | Default: ''
			use_wpa3(bool, optional): O | Use wpa3 security protocol | Default: False
			listen_interval(int, optional) : O | Number of AP beacons station will sleep | Default:3
			band_mode(int, optional): O | Connect on 2.4G (1) or 5G (2) band, or Auto select (3) | Default:3

		Returns:
			ctrl_cmd: ctrl_cmd object
		"""

		if process_is_param_missing(ssid):
			self.out = "Missing param " + "--ssid"
			return self

		self.out = process_connect_ap(ssid, pwd, bssid, use_wpa3, listen_interval, band_mode)
		return self


	def get_connected_ap_info(self):
		"""Get info of connected AP (Wi-Fi router or hotspot)

		Args:
			no_arg(str,optional): O | Dummy arg

		Returns:
			ctrl_cmd: ctrl_cmd object
		"""
		self.out = process_get_connected_ap_info()
		return self


	def disconnect_ap(self, reset_dhcp : bool = True):
		"""Disconnect from AP (Wi-Fi router or hotspot)

		Args:
			reset_dhcp(bool, optional): O | Clean DHCP DHCP | Default: True

		Returns:
			ctrl_cmd: ctrl_cmd object
		"""
		self.out = process_disconnect_ap(reset_dhcp)
		return self


	def softap_vendor_ie(self, enable : bool = "True", data: str = ""):
		"""Set vendor specific IE in softap beacon
		   Once vendor IE is set, it cannot be set again unless it is reset first

		Args:
			enable(bool, mandatory): M | Values ['yes' | 'no'] Set or Reset Vendor IE
			data(bool, optional): O | String to set in softap Wi-Fi broadcast beacon | Default: ''

		Returns:
			ctrl_cmd: ctrl_cmd object
		"""

		if process_is_param_missing(enable):
			self.out = "Missing param " + "--enable"
			return self

		self.out = process_softap_vendor_ie(enable,data)
		return self


	def start_softap(self, ssid : str = "", pwd : str = "", channel : int = 1, sec_prot: str = "wpa_wpa2_psk", max_conn: int = 4, hide_ssid: bool = False, bw : int = 20, start_dhcp_server : bool = True, band_mode: int = WIFI_BAND_MODE_AUTO):
		"""Connect to AP (Wi-Fi router or hotspot)

		Args:
			ssid (str, mandatory): M | SSID to configure ESP softAP
			pwd(str, mandatory): M | Password to configure ESP softAP
			channel(int, optional): O | Wi-Fi channel [ 1 to 11] | Default: 1
			sec_prot(str, optional): O | Security Protocol or authentication protocol ['open' | 'wpa_psk' | 'wpa2_psk' | 'wpa_wpa2_psk'] | Default: 'wpa_wpa2_psk'
			max_conn(int, optional) : O | Max num of stations that can connect | Default:4
			hide_ssid(bool, optional): O | Hide SSID broadcasting [ True | False ] | Default: False
			bw(int, optional): O | Wi-Fi Bandwidth [ 20 | 40 ] | Default: 20
			start_dhcp_server(bool, optional): O | Start DHCP server | Default: True
			band_mode(int, optional): O | Connect on 2.4G (1) or 5G (2) band, or Auto select (3) | Default:3

		Returns:
			ctrl_cmd: ctrl_cmd object
		"""

		if process_is_param_missing(ssid):
			self.out = "Missing param " + "--ssid"
			return self
		if process_is_param_missing(pwd):
			self.out = "Missing param " + "--pwd"
			return self

		self.out = process_start_softap(ssid, pwd, channel, sec_prot, max_conn, hide_ssid, bw, start_dhcp_server, band_mode)
		return self


	def get_softap_info(self):
		"""Get info of ESP softAP

		Args:
			no_arg(str,optional): O | Dummy arg

		Returns:
			ctrl_cmd: ctrl_cmd object
		"""
		self.out = process_get_softap_info()
		return self


	def softap_connected_clients_info(self):
		"""Get stations info which are connected to ESP softAP

		Args:
			no_arg(str,optional): O | Dummy arg

		Returns:
			ctrl_cmd: ctrl_cmd object
		"""
		self.out = process_softap_connected_clients_info()
		return self


	def stop_softap(self):
		"""Stop ESP softAP

		Args:
			no_arg(str,optional): O | Dummy arg

		Returns:
			ctrl_cmd: ctrl_cmd object
		"""
		self.out = process_stop_softap()
		return self


	def set_wifi_power_save(self, mode : str = "max"):
		"""Set Wi-Fi power save

		Args:
			mode(str,optional): O | power save mode ['none','min','max'] | Default: 'max'

		Returns:
			ctrl_cmd: ctrl_cmd object
		"""
		self.out = process_set_power_save(mode)
		return self


	def get_wifi_power_save(self):
		"""Get current Wi-Fi power save

		Args:
			no_arg(str,optional): O | Dummy arg

		Returns:
			ctrl_cmd: ctrl_cmd object
		"""
		self.out = process_get_power_save()
		return self


	def set_wifi_max_tx_power(self, map_val : int = 0):
		"""Set Wi-Fi maximum TX power
		Please note this is just request, firmware may set maximum possible from input power

		Args:
			map_val(int,mandatory): M | Set Wi-Fi max power in map value

		Returns:
			ctrl_cmd: ctrl_cmd object
		"""

		if process_is_param_missing(map_val):
			self.out = "Missing param " + "--map_val"
			return self

		self.out = process_set_wifi_max_tx_power(map_val)
		return self


	def get_wifi_curr_tx_power(self):
		"""Get current Wi-Fi TX power

		Args:
			no_arg(str,optional): O | Dummy arg

		Returns:
			ctrl_cmd: ctrl_cmd object
		"""
		self.out = process_wifi_curr_tx_power()
		return self

	def enable_wifi(self):
		"""Enable Wi-Fi

		Args:
			no_arg(str,optional): O | Dummy arg

		Returns:
			ctrl_cmd: ctrl_cmd object
		"""
		self.out = process_enable_wifi()
		return self

	def disable_wifi(self):
		"""Disable Wi-Fi

		Args:
			no_arg(str,optional): O | Dummy arg

		Returns:
			ctrl_cmd: ctrl_cmd object
		"""
		self.out = process_disable_wifi()
		return self

	def enable_bt(self):
		"""Enable Bluetooth

		Args:
			no_arg(str,optional): O | Dummy arg

		Returns:
			ctrl_cmd: ctrl_cmd object
		"""
		self.out = process_enable_bluetooth()
		return self

	def disable_bt(self):
		"""Disable Bluetooth

		Args:
			no_arg(str,optional): O | Dummy arg

		Returns:
			ctrl_cmd: ctrl_cmd object
		"""
		self.out = process_disable_bluetooth()
		return self

	def get_fw_version(self):
		"""Get Firmware Version

		Args:
			no_arg(str,optional): O | Dummy arg

		Returns:
			ctrl_cmd: ctrl_cmd object
		"""
		self.out = process_get_fw_version()
		return self

	def set_country_code(self, country : str = "01 ", ieee80211d_enabled : bool = True):
		"""Set Country Code

		Sets the Wi-Fi Country Code

		"country" is three octets, consisting of a two octet country code and a regulatory octet

		Supported country codes are "01"(world safe mode) "AT","AU","BE","BG","BR", "CA","CH","CN","CY","CZ","DE","DK","EE","ES","FI","FR","GB","GR","HK","HR","HU", "IE","IN","IS","IT","JP","KR","LI","LT","LU","LV","MT","MX","NL","NO","NZ","PL","PT", "RO","SE","SI","SK","TW","US"

		The third octet is one of the following:
		- an ASCII space character, which means the regulations under which the station/AP is operating encompass all environments for the current frequency band in the country.
		- an ASCII 'O' character, which means the regulations under which the station/AP is operating are for an outdoor environment only.
		- an ASCII 'I' character, which means the regulations under which the station/AP is operating are for an indoor environment only.
		- an ASCII 'X' character, which means the station/AP is operating under a noncountry entity. The first two octets of the noncountry entity is two ASCII 'XX' characters.

		Args:
			country (str, mandatory): M | Country Code to set
			ieee80211d_enabled (bool, optional): O | Use Country Code of AP when station is connected | Default: True

		Returns:
			ctrl_cmd: ctrl_cmd object
		"""
		self.out = process_set_country_code(country, ieee80211d_enabled)
		return self

	def get_country_code(self):
		"""Get Country Code

		Args:
			no_arg(str,optional): O | Dummy arg

		Returns:
			ctrl_cmd: ctrl_cmd object
		"""
		self.out = process_get_country_code()
		return self

	def ota_update(self, url : str = ""):
		"""OTA update with HTTP link

		Args:
			url(str,mandatory): M | URL of ESP firmware binary 'network_adapter.bin'

		Returns:
			ctrl_cmd: ctrl_cmd object
		"""

		if process_is_param_missing(url):
			self.out = "Missing param " + "--url"
			return self

		self.out = process_ota_update(url)
		return self


	def heartbeat(self, enable: bool = True, duration: int = 30):
		"""Configure Heartbeat

		Args:
			enable(bool,optional): O | Values ['True' | 'False'] | Default: True
			duration(int,optional): O | Heartbeat duration in sec | Default: 30

		Returns:
			ctrl_cmd: ctrl_cmd object
		"""
		self.out = process_heartbeat(enable, duration)
		return self


	def subscribe_event(self, event: str = ""):
		"""Subscribe event to get notifications

		Args:
			event(str,mandatory): M | Values ['esp_init' | 'heartbeat' | 'sta_connected' | 'sta_disconnected' | 'softap_sta_connected' | 'softap_sta_disconnected' | 'dhcp_dns_status' | 'custom_packed_event' | 'all' ]

		Returns:
			ctrl_cmd: ctrl_cmd object
		"""

		if process_is_param_missing(event):
			self.out = "Missing param " + "--event"
			return self

		self.out = process_subscribe_event(event)
		return self


	def unsubscribe_event(self, event: str = ""):
		"""Unsubscribe event to get notifications

		Args:
			event(str,mandatory): M | Values ['esp_init' | 'heartbeat' | 'sta_connected' | 'sta_disconnected' | 'softap_sta_connected' | 'softap_sta_disconnected' | 'dhcp_dns_status' | 'custom_packed_event' | 'all' ]

		Returns:
			ctrl_cmd: ctrl_cmd object
		"""

		if process_is_param_missing(event):
			self.out = "Missing param " + "--event"
			return self

		self.out = process_unsubscribe_event(event)
		return self

	def custom_rpc_demo1(self):
		"""Send a custom RPC request with only acknowledgement (No echo back response)

		This demo shows how to send a custom RPC request that expects only an acknowledgement.
		No specific data is expected in response.

		Returns:
			success/failure: Result of the operation
		"""
		return process_custom_rpc_demo1()

	def custom_rpc_demo2(self):
		"""Send a custom RPC request and get echo back as response

		This demo shows how to send a custom RPC request with data
		and receive an echo back response. The response is verified to be
		the same as the sent data.

		Returns:
			success/failure: Result of the operation
		"""
		return process_custom_rpc_demo2()

	def custom_rpc_demo3(self):
		"""Send a custom RPC request and get echo back as event

		This demo shows how to send a custom RPC request with data
		and receive an echo back as an event. The event data is verified
		in the event handler.

		Returns:
			success/failure: Result of the operation
		"""
		return process_custom_rpc_demo3()

CONFIG_BT_ENABLED := y
CONFIG_TEST_RAW_TP := n
CONFIG_INFO_LOGS=y
CONFIG_DEBUG_LOGS=n
CONFIG_VERBOSE_LOGS=n

# In case of SDIO as transport, one of slave chipset used,
# CONFIG_TARGET_ESP32  OR
# CONFIG_TARGET_ESP32C6
# need to be added depending upon slave in use
# rpi_init.sh will add that flag using ESP_SLAVE
ESP_SLAVE := ""

# Toolchain Path
CROSS_COMPILE :=
# Linux Kernel header
KERNEL := /lib/modules/$(shell uname -r)/build
# Architecture
ARCH := arm64

#Default interface is sdio
MODULE_NAME=esp32_sdio

#Targets passed overrrides default value
ifeq ($(target), sdio)
	MODULE_NAME=esp32_sdio
endif

ifeq ($(target), spi)
	MODULE_NAME=esp32_spi
endif

ifeq ($(CONFIG_TEST_RAW_TP), y)
	EXTRA_CFLAGS += -DCONFIG_TEST_RAW_TP
endif

ifeq ($(CONFIG_BT_ENABLED), y)
	EXTRA_CFLAGS += -DCONFIG_BT_ENABLED
	module_objects += esp_bt.o
endif

EXTRA_CFLAGS += -I$(PWD)/../../../../common/include -I$(PWD)

ifeq ($(MODULE_NAME), esp32_sdio)
	EXTRA_CFLAGS += -I$(PWD)/sdio
	module_objects += sdio/esp_sdio.o sdio/esp_sdio_api.o
endif

ifeq ($(MODULE_NAME), esp32_spi)
	EXTRA_CFLAGS += -I$(PWD)/spi
	module_objects += spi/esp_spi.o
endif

ifneq ($(ESP_SLAVE), "")
EXTRA_CFLAGS += -D$(ESP_SLAVE)
endif

ifeq ($(CONFIG_INFO_LOGS), y)
	EXTRA_CFLAGS += -DCONFIG_INFO_LOGS
endif

ifeq ($(CONFIG_DEBUG_LOGS), y)
	EXTRA_CFLAGS += -DCONFIG_INFO_LOGS
	EXTRA_CFLAGS += -DCONFIG_DEBUG_LOGS
endif

ifeq ($(CONFIG_VERBOSE_LOGS), y)
	EXTRA_CFLAGS += -DCONFIG_INFO_LOGS
	EXTRA_CFLAGS += -DCONFIG_DEBUG_LOGS
	EXTRA_CFLAGS += -DCONFIG_VERBOSE_LOGS
endif

PWD := $(shell pwd)

obj-m := $(MODULE_NAME).o
$(MODULE_NAME)-y := main.o esp_stats.o $(module_objects)
$(MODULE_NAME)-y += esp_serial.o esp_rb.o esp_fw_verify.o

all: clean
	make ARCH=$(ARCH) CROSS_COMPILE=$(CROSS_COMPILE) -C $(KERNEL) M=$(PWD) modules

clean:
	rm -rf *.o sdio/*.o spi/*.o *.ko
	make ARCH=$(ARCH) CROSS_COMPILE=$(CROSS_COMPILE) -C $(KERNEL) M=$(PWD) clean

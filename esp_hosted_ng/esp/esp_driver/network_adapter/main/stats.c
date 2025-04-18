// SPDX-License-Identifier: Apache-2.0
// Copyright 2015-2022 Espressif Systems (Shanghai) PTE LTD
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at

//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//

#include "stats.h"
#include <unistd.h>
#include "esp_log.h"
#include "esp.h"
#include "slave_bt.h"
#include "cmd.h"
#include "esp_fw_version.h"
#include <string.h>
#include "esp_private/wifi.h"
#include <inttypes.h>

static const char TAG[] = "stats";

#ifdef CONFIG_FREERTOS_GENERATE_RUN_TIME_STATS
/* These functions are only for debugging purpose
 * Please do not enable in production environments
 */
static esp_err_t log_real_time_stats(TickType_t xTicksToWait)
{
    TaskStatus_t *start_array = NULL, *end_array = NULL;
    UBaseType_t start_array_size, end_array_size;
    uint32_t start_run_time, end_run_time;
    esp_err_t ret;

    /*Allocate array to store current task states*/
    start_array_size = uxTaskGetNumberOfTasks() + ARRAY_SIZE_OFFSET;
    start_array = malloc(sizeof(TaskStatus_t) * start_array_size);
    if (start_array == NULL) {
        ret = ESP_ERR_NO_MEM;
        goto exit;
    }
    /*Get current task states*/
    start_array_size = uxTaskGetSystemState(start_array, start_array_size, &start_run_time);
    if (start_array_size == 0) {
        ret = ESP_ERR_INVALID_SIZE;
        goto exit;
    }

    vTaskDelay(xTicksToWait);

    /*Allocate array to store tasks states post delay*/
    end_array_size = uxTaskGetNumberOfTasks() + ARRAY_SIZE_OFFSET;
    end_array = malloc(sizeof(TaskStatus_t) * end_array_size);
    if (end_array == NULL) {
        ret = ESP_ERR_NO_MEM;
        goto exit;
    }
    /*Get post delay task states*/
    end_array_size = uxTaskGetSystemState(end_array, end_array_size, &end_run_time);
    if (end_array_size == 0) {
        ret = ESP_ERR_INVALID_SIZE;
        goto exit;
    }

    /*Calculate total_elapsed_time in units of run time stats clock period.*/
    uint32_t total_elapsed_time = (end_run_time - start_run_time);
    if (total_elapsed_time == 0) {
        ret = ESP_ERR_INVALID_STATE;
        goto exit;
    }

    ESP_LOGI(TAG, "| Task | Run Time | Percentage");
    /*Match each task in start_array to those in the end_array*/
    for (int i = 0; i < start_array_size; i++) {
        int k = -1;
        for (int j = 0; j < end_array_size; j++) {
            if (start_array[i].xHandle == end_array[j].xHandle) {
                k = j;
                /*Mark that task have been matched by overwriting their handles*/
                start_array[i].xHandle = NULL;
                end_array[j].xHandle = NULL;
                break;
            }
        }
        /*Check if matching task found*/
        if (k >= 0) {
            uint32_t task_elapsed_time = end_array[k].ulRunTimeCounter - start_array[i].ulRunTimeCounter;
            uint32_t percentage_time = (task_elapsed_time * 100UL) / (total_elapsed_time * portNUM_PROCESSORS);
            ESP_LOGI(TAG, "| %s | %"PRIu32" | %"PRIu32"%%", start_array[i].pcTaskName, task_elapsed_time, percentage_time);
        }
    }

    /*Print unmatched tasks*/
    for (int i = 0; i < start_array_size; i++) {
        if (start_array[i].xHandle != NULL) {
            ESP_LOGI(TAG, "| %s | Deleted", start_array[i].pcTaskName);
        }
    }
    for (int i = 0; i < end_array_size; i++) {
        if (end_array[i].xHandle != NULL) {
            ESP_LOGI(TAG, "| %s | Created", end_array[i].pcTaskName);
        }
    }
    ret = ESP_OK;

exit:    /*Common return path*/
    if (start_array) {
        free(start_array);
    }
    if (end_array) {
        free(end_array);
    }
    return ret;
}

static void log_runtime_stats_task(void* pvParameters)
{
    while (1) {
        ESP_LOGI(TAG, "\n\nGetting real time stats over %"PRIu32" ticks", STATS_TICKS);
        if (log_real_time_stats(STATS_TICKS) == ESP_OK) {
            ESP_LOGI(TAG, "Real time stats obtained");
        } else {
            ESP_LOGE(TAG, "Error getting real time stats");
        }
        vTaskDelay(pdMS_TO_TICKS(1000 * 2));
    }
}
#endif

uint8_t raw_tp_tx_buf[TEST_RAW_TP__BUF_SIZE] = {0};
uint64_t test_raw_tp_rx_len;

void debug_update_raw_tp_rx_count(uint16_t len)
{
    test_raw_tp_rx_len += len;
}

static void raw_tp_timer_func(void* arg)
{
    static int32_t cur = 0;
    double actual_bandwidth = 0;
    int32_t div = 1024;

    actual_bandwidth = (test_raw_tp_rx_len * 8);
    ESP_LOGI(TAG, "%ld-%ld sec       %.2f kbits/sec", cur, cur + 1, actual_bandwidth / div);
    cur++;
    test_raw_tp_rx_len = 0;
}

extern volatile uint8_t datapath;
static void raw_tp_tx_task(void* pvParameters)
{
    int ret;
    interface_buffer_handle_t buf_handle = {0};

    for (;;) {

        if (!datapath) {
            sleep(1);
            continue;
        }

        buf_handle.if_type = ESP_TEST_IF;
        buf_handle.if_num = 0;

        buf_handle.payload = raw_tp_tx_buf;
        buf_handle.payload_len = TEST_RAW_TP__BUF_SIZE;

        ret = send_to_host(PRIO_Q_LOW, &buf_handle);

        if (!ret) {
            ESP_LOGE(TAG, "Failed to send to queue");
            continue;
        }
        test_raw_tp_rx_len += (TEST_RAW_TP__BUF_SIZE + sizeof(struct esp_payload_header));
    }
}

static void start_timer_to_display_raw_tp(void)
{
    test_args_t args = {0};
    esp_timer_handle_t raw_tp_timer = {0};
    esp_timer_create_args_t create_args = {
        .callback = &raw_tp_timer_func,
        .arg = &args,
        .name = "raw_tp_timer",
    };

    ESP_ERROR_CHECK(esp_timer_create(&create_args, &raw_tp_timer));

    args.timer = raw_tp_timer;

    ESP_ERROR_CHECK(esp_timer_start_periodic(raw_tp_timer, TEST_RAW_TP__TIMEOUT));
}

void create_debugging_tasks(void)
{
#ifdef CONFIG_FREERTOS_GENERATE_RUN_TIME_STATS
    assert(xTaskCreate(log_runtime_stats_task, "log_runtime_stats_task",
                       TASK_DEFAULT_STACK_SIZE, NULL, TASK_DEFAULT_PRIO, NULL) == pdTRUE);
#endif
}

void init_raw_tp_test_task(void)
{
    assert(xTaskCreate(raw_tp_tx_task, "raw_tp_tx_task",
                       TASK_DEFAULT_STACK_SIZE, NULL, TASK_DEFAULT_PRIO, NULL) == pdTRUE);
}

void init_raw_tp_timer(void)
{
    start_timer_to_display_raw_tp();
}

void debug_get_raw_tp_conf(uint32_t raw_tp_type)
{
    if (raw_tp_type == CMD_RAW_TP_ESP_TO_HOST) {
        ESP_LOGI(TAG, "\n\n*** Raw Throughput testing: ESP --> Host started ***\n");
    } else if (raw_tp_type == CMD_RAW_TP_HOST_TO_ESP) {
        ESP_LOGI(TAG, "\n\n*** Raw Throughput testing: Host --> ESP started ***\n");
    }
}

void debug_set_wifi_logging(void)
{
    /* set WiFi log level and module */
    uint32_t wifi_log_level = WIFI_LOG_INFO;
#if CONFIG_LOG_MAXIMUM_LEVEL == 0
    wifi_log_level = WIFI_LOG_NONE;
#elif CONFIG_LOG_MAXIMUM_LEVEL == 1
    wifi_log_level = WIFI_LOG_ERROR;
#elif CONFIG_LOG_MAXIMUM_LEVEL == 2
    wifi_log_level = WIFI_LOG_WARNING;
#elif CONFIG_LOG_MAXIMUM_LEVEL == 3
    wifi_log_level = WIFI_LOG_INFO;
#elif CONFIG_LOG_MAXIMUM_LEVEL == 4
    wifi_log_level = WIFI_LOG_DEBUG;
#elif CONFIG_LOG_MAXIMUM_LEVEL == 5
    wifi_log_level = WIFI_LOG_VERBOSE;
#endif
    esp_wifi_internal_set_log_level(wifi_log_level);
}

void debug_log_firmware_version(void)
{
    ESP_LOGI(TAG, "*********************************************************************");
    ESP_LOGI(TAG, "                ESP-Hosted Firmware version :: %s-%d.%d.%d.%d.%d                        ",
             PROJECT_NAME, PROJECT_VERSION_MAJOR_1, PROJECT_VERSION_MAJOR_2, PROJECT_VERSION_MINOR, PROJECT_REVISION_PATCH_1, PROJECT_REVISION_PATCH_2);

#if CONFIG_ESP_SPI_HOST_INTERFACE
#if BLUETOOTH_UART
    ESP_LOGI(TAG, "                Transport used :: SPI + UART                    ");
#else
    ESP_LOGI(TAG, "                Transport used :: SPI only                      ");
#endif
#else
#if BLUETOOTH_UART
    ESP_LOGI(TAG, "                Transport used :: SDIO + UART                   ");
#else
    ESP_LOGI(TAG, "                Transport used :: SDIO only                     ");
#endif
#endif
    ESP_LOGI(TAG, "*********************************************************************");
}

int process_raw_tp(uint8_t if_type, uint8_t *payload, uint16_t payload_len)
{
    interface_buffer_handle_t buf_handle = {0};
    esp_err_t ret = ESP_OK;
    struct command_header *header = (struct command_header *) payload;
    struct command_header *resp_header;

    buf_handle.if_type = if_type;
    buf_handle.if_num = 0;
    buf_handle.payload_len = sizeof(struct command_header);
    buf_handle.pkt_type = PACKET_TYPE_COMMAND_RESPONSE;

    buf_handle.payload = heap_caps_malloc(buf_handle.payload_len, MALLOC_CAP_DMA);
    assert(buf_handle.payload);
    memset(buf_handle.payload, 0, buf_handle.payload_len);
    resp_header = (struct command_header *) buf_handle.payload;

    debug_get_raw_tp_conf(header->cmd_code);
    init_raw_tp_timer();

    if (header->cmd_code == CMD_RAW_TP_ESP_TO_HOST) {
        init_raw_tp_test_task();
    }

    resp_header->cmd_code = header->cmd_code;
    resp_header->len = 0;
    resp_header->cmd_status = CMD_RESPONSE_SUCCESS;

    buf_handle.priv_buffer_handle = buf_handle.payload;
    buf_handle.free_buf_handle = free;

    ret = send_command_response(&buf_handle);
    if (ret != pdTRUE) {
        ESP_LOGE(TAG, "Slave -> Host: Failed to send command response\n");
        goto DONE;
    }

    return ESP_OK;

DONE:
    if (buf_handle.payload) {
        free(buf_handle.payload);
    }

    return ret;
}

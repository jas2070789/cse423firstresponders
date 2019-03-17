#include "bluetooth_char.h"

tBleStatus Seconds_Update(void)
{
 uint32_t val;
 tBleStatus ret;

 //Obtain system tick value in milliseconds
 val = GetTick();
 val = val/1000;//convert to sec


 const uint8_t time[4] = {(val >> 24)&0xFF, (val >> 16)&0xFF, (val >> 8)&0xFF,
(val)&0xFF};	//update GATT value
 
 ret = aci_gatt_update_char_value(timeServHandle, secondsCharHandle, 0, 4,
 time);

 if (ret != STATUS_SUCCESS){
 PRINTF("Error while updating TIME characteristic.\n") ;
 return BLE_STATUS_ERROR ;
 }
 return BLE_STATUS_SUCCESS;
}
 

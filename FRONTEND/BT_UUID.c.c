#include "BT_uuid.h"

tBleStatus Add_Time_Service(void)
{
 tBleStatus ret;
 uint8_t uuid[16];

 COPY_TIME_SERVICE_UUID(uuid);

 ret = aci_gatt_add_serv(UUID_TYPE_128, uuid, PRIMARY_SERVICE, 7,
 &timeServHandle);	//add time service to GATT server
	
 if (ret != STATUS_SUCCESS) goto fail;	//for debugging, delete later

 COPY_TIME_UUID(uuid);
 
 ret = aci_gatt_add_char(timeServHandle, UUID_TYPE_128, uuid, 4,
 CHAR_PROP_READ, ATTR_PERMISSION_NONE, 0,&secondsCharHandle);	//ubtain a char according to the UUID
if (ret != STATUS_SUCCESS) goto fail;

 COPY_MINUTE_UUID(uuid);
 
 ret = aci_gatt_add_char(timeServHandle, UUID_TYPE_128, uuid, 4,
 CHAR_PROP_NOTIFY|CHAR_PROP_READ, 0, &minuteCharHandle);//send char to time service
 if (ret != STATUS_SUCCESS) goto fail;

 return STATUS_SUCCESS;

fail:
 PRINTF("Error while sending char.\n");
 return STATUS_ERROR ;
}
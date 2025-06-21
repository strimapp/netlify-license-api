# netlify/functions/validate.py
import json
import os
import datetime
from supabase import create_client, Client

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def handler(event, context):
    try:
        data = json.loads(event['body'])
        key_to_check = data.get('license_key')

        if not key_to_check:
            return {
                "statusCode": 400,
                "body": json.dumps({"valid": False, "message": "Kunci lisensi tidak disediakan."})
            }

        response = supabase.table('licenses').select('*').eq('license_key', key_to_check).execute()

        if response.data:
            license_info = response.data[0]
            expiry_date_str = license_info.get('expiry_date')
            expiry_date = datetime.datetime.strptime(expiry_date_str, '%Y-%m-%d').date()

            if datetime.date.today() <= expiry_date:
                return {
                    "statusCode": 200,
                    "body": json.dumps({
                        "valid": True,
                        "message": f"Lisensi aktif hingga {expiry_date.strftime('%d %B %Y')}"
                    })
                }
            else:
                return {
                    "statusCode": 403,
                    "body": json.dumps({
                        "valid": False,
                        "message": f"Lisensi sudah kedaluwarsa pada {expiry_date.strftime('%d %B %Y')}"
                    })
                }
        else:
            return {
                "statusCode": 404,
                "body": json.dumps({"valid": False, "message": "Kunci lisensi tidak valid."})
            }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"valid": False, "message": "Terjadi error di server."})
        }

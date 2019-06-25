def event_descriptor(event_id, modification_number, modification_date_time, priority,
                     market_context, created_date_time, event_status, test_event, vtn_comment):
    data = {"event_id": event_id,
            "modification_number": modification_number,
            "modification_date_time": modification_date_time,
            "priority": priority,
            "market_context": market_context,
            "created_date_time": created_date_time,
            "event_status": event_status,
            "test_event": test_event,
            "vtn_comment": vtn_comment}
    return {key: value for key, value in data.items() if value}

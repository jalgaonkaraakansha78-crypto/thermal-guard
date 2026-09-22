from apscheduler.schedulers.blocking import BlockingScheduler
from app.core.config import get_settings
from app.db.database import SessionLocal, init_db
from app.services.pipeline import run_live
from app.db.models import Event

def ingest():
    s=get_settings()
    if not s.firms_map_key: print("FIRMS_MAP_KEY missing; skipping live ingest"); return
    try:
        _,_,events=run_live(); db=SessionLocal()
        for _,r in events.iterrows():
            if not db.query(Event).filter(Event.event_id==r.event_id).first():
                db.add(Event(event_id=r.event_id,latitude=r.latitude,longitude=r.longitude,detection_count=r.detection_count,frp_max=r.frp_max,frp_mean=r.frp_mean,frp_sum=r.frp_sum,confidence_mean=r.confidence_mean,bright_ti4_max=r.bright_ti4_max,bright_ti4_mean=r.bright_ti4_mean,first_seen=r.first_seen,last_seen=r.last_seen,duration_minutes=r.duration_minutes))
        db.commit(); db.close(); print(f"Ingested {len(events)} events")
    except Exception as e: print(f"Live ingest failed: {e}")

if __name__=="__main__":
    init_db(); s=get_settings(); scheduler=BlockingScheduler(); scheduler.add_job(ingest,"interval",minutes=s.poll_minutes,next_run_time=None); ingest(); scheduler.start()

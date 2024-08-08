from ambient_wx import AmbientApi, WxDeviceCollection
from dotenv import dotenv_values
from apscheduler.schedulers.blocking import BlockingScheduler
import psycopg2 as pg2


class Database:
  def __init__(self, host, db, username, password, port=5432):
    self.host = host
    self.db = db
    self.username = username
    self.password = password
    self.port = port
    self.cur = None
    self.conn = None

  def connect(self):
    self.conn = pg2.connect(host=self.host, database=self.db, user=self.username, password=self.password, port=self.port)
    self.cur = self.conn.cursor()

  def execute_query(self, query):
    self.cur.execute(query)
    self.conn.commit()

  def close(self):
    self.cur.close()
    self.conn.close()


def convert_in_to_mb(pressure):
    conversion_factor = 33.863889532610884
    return round(pressure*conversion_factor, 2)


def generate_query(data):
   fields = [
    "api_datetime",
    "temp_f",
    "dew_point_f",
    "feels_like_f",
    "temp_c",
    "dew_point_c",
    "feels_like_c",
    "wind_speed_mph",
    "wind_gust_mph",
    "max_daily_gust_mph",
    "wind_speed_kph",
    "wind_gust_kph",
    "max_daily_gust_kph",
    "hourly_rain_in",
    "daily_rain_in",
    "hourly_rain_cm",
    "daily_rain_cm",
    "wind_dir",
    "wind_dir_avg10m",
    "humidity",
    "barometric_pressure_in",
    "barometric_pressure_mb"
   ]
   values_in_order = [f"timestamp '{data[field]}'" if field=="api_datetime" else str(data[field]) for field in fields]
   insert_sql_prefix = f"""INSERT INTO weather ({",".join(fields)}) VALUES\n"""
   insert_sql_values = f"({','.join(values_in_order)});"
   return insert_sql_prefix + insert_sql_values


def get_data():
    # creds = dict(dotenv_values(".env"))
    # api = AmbientApi(api_key=creds["AMBIENT_API_KEY"], application_key=creds["AMBIENT_APPLICATION_KEY"])
    # devices = WxDeviceCollection(api)
    # devices.get_devices()
    # device = devices.devices[0]
    # data = device.data
    # data_collect = {}
    # data_collect["api_datetime"] = data.date
    # data_collect["temp_f"] =data.tempf.magnitude
    # data_collect["dew_point_f"] =data.dewPoint.magnitude
    # data_collect["feels_like_f"] =data.feelsLike.magnitude
    # data_collect["temp_c"] = round(data.tempf.to('degC').magnitude,2)
    # data_collect["dew_point_c"] =round(data.dewPoint.to('degC').magnitude,2)
    # data_collect["feels_like_c"] =round(data.feelsLike.to('degC').magnitude,2)
    # data_collect["wind_speed_mph"] =data.windspeedmph.magnitude
    # data_collect["wind_gust_mph"] =data.windgustmph.magnitude
    # data_collect["max_daily_gust_mph"] =data.maxdailygust.magnitude
    # data_collect["wind_speed_kt"] = round(data.windspeedmph.to('kt').magnitude,2)
    # data_collect["wind_gust_kt"] = round(data.windgustmph.to('kt').magnitude,2)
    # data_collect["max_daily_gust_kt"] = round(data.maxdailygust.to('kt').magnitude,2)
    # data_collect["hourly_rain_in"] = 0 if data.hourlyrainin is None else data.hourlyrainin.magnitude
    # data_collect["daily_rain_in"] = 0 if data.dailyrainin is None else data.dailyrainin.magnitude
    # data_collect["hourly_rain_cm"] = 0 if data.hourlyrainin is None else round(data.hourlyrainin.to('cm').magnitude,2)
    # data_collect["daily_rain_cm"] = 0 if data.dailyrainin is None else round(data.dailyrainin.to('cm').magnitude,2)
    # data_collect["wind_dir"] = data.winddir.magnitude
    # data_collect["wind_dir_avg10m"] = data.winddir_avg10m.magnitude
    # data_collect["humidity"] = data.humidity.magnitude
    # data_collect["barometric_pressure_in"] = data.baromrelin.magnitude
    # data_collect["barometric_pressure_mb"] = convert_in_to_mb(data.baromrelin.magnitude)
    # db = Database(host='db', db="station", username="postgres", password="postgres")
    # db.connect()
    # insert_sql = generate_query(data_collect)
    # db.execute_query(insert_sql)
    # db.close()
    pass



if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(get_data, 'cron', minute='*', hour='*', day='*', year='*', month='*')
    scheduler.start()

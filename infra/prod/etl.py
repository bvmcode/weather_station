from ambient_wx import AmbientApi, WxDeviceCollection
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
import psycopg2 as pg2
import os

load_dotenv()

class Database:
  def __init__(self):
    self.host = os.getenv("POSTGRES_HOST")
    self.db = os.getenv("POSTGRES_DB")
    self.username = os.getenv("POSTGRES_USER")
    self.password = os.getenv("POSTGRES_PWD")
    self.port = 5432
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
    "wind_speed_kt",
    "wind_gust_kt",
    "max_daily_gust_kt",
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


def value_or_zero(value, zero_value, conversion=None):
   try:
      if conversion:
        return round(value.to(conversion).magnitude, 2)
      else:
        return round(value.magnitude, 2)
   except AttributeError:
      return zero_value


def get_data():
    api = AmbientApi(api_key=os.getenv("AMBIENT_API_KEY"), application_key=os.getenv("AMBIENT_APPLICATION_KEY"))
    devices = WxDeviceCollection(api)
    devices.get_devices()
    device = devices.devices[0]
    data = device.data
    data_collect = {}
    data_collect["api_datetime"] = data.date
    data_collect["temp_f"] =data.tempf.magnitude
    data_collect["dew_point_f"] =data.dewPoint.magnitude
    data_collect["feels_like_f"] =data.feelsLike.magnitude
    data_collect["temp_c"] = value_or_zero(data.tempf, 0, 'degC')
    data_collect["dew_point_c"] = value_or_zero(data.dewPoint, 0, 'degC')
    data_collect["feels_like_c"] = value_or_zero(data.feelsLike, 0, 'degC')
    data_collect["wind_speed_mph"] = value_or_zero(data.windspeedmph, 0)
    data_collect["wind_gust_mph"] = value_or_zero(data.windgustmph, 0)
    data_collect["max_daily_gust_mph"] = value_or_zero(data.maxdailygust, 0)
    data_collect["wind_speed_kt"] = value_or_zero(data.windspeedmph, 0, 'kt')
    data_collect["wind_gust_kt"] = value_or_zero(data.windgustmph, 0, 'kt')
    data_collect["max_daily_gust_kt"] = value_or_zero(data.maxdailygust, 0,'kt')
    data_collect["hourly_rain_in"] = value_or_zero(data.hourlyrainin, 0)
    data_collect["daily_rain_in"] = value_or_zero(data.dailyrainin, 0)
    data_collect["hourly_rain_cm"] = value_or_zero(data.hourlyrainin, 0, 'cm')
    data_collect["daily_rain_cm"] = value_or_zero(data.dailyrainin, 0, 'cm')
    data_collect["wind_dir"] = value_or_zero(data.winddir, None)
    data_collect["wind_dir_avg10m"] = value_or_zero(data.winddir_avg10m, None)
    data_collect["humidity"] = data.humidity.magnitude
    data_collect["barometric_pressure_in"] = data.baromrelin.magnitude
    data_collect["barometric_pressure_mb"] = convert_in_to_mb(data.baromrelin.magnitude)
    db = Database()
    db.connect()
    insert_sql = generate_query(data_collect)
    db.execute_query(insert_sql)
    db.close()



if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(get_data, 'cron', minute='*/5', hour='*', day='*', year='*', month='*')
    scheduler.start()

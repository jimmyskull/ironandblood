import datetime

class Config:
  # Initial date in game-time
  start_epoch = datetime.datetime(1800, 1, 31, 0, 0, 0)
  # Initial date in real-time
  start_date = datetime.datetime(2016, 3, 31, 0, 0, 0)

  @staticmethod
  def current_game_date():
    return Config.to_game_date(datetime.datetime.now())

  @staticmethod
  def to_game_date(date):
    """
    Returns the game-time date.
    1 turn = 1 game-time year = 1 real-time day.
    """
    seconds = (date - Config.start_date).total_seconds()
    norm = 0.004224537037037037 # 1s / (60s * 60m) / 24h * 365d
    return Config.start_epoch + datetime.timedelta(days = seconds * norm)


class Status(object):

  __definitions = {0 : 'Draft',
                     1 : 'Confirmed',
                     2 : 'Expired',
                     3 : 'Deleted'}
    
  @staticmethod
  def getByID(identifier):
    try:
      identifier = int(identifier)

      if identifier >= 0 and identifier <= len(Status.__definitions):
        return Status.__definitions[identifier]
    except Exception:
      pass

    raise Exception('Invalid input "{0}"'.format(identifier))

  @staticmethod
  def getByName(name):
    try:
      formattedInput = str(name).title()

      for key, value in Status.__definitions.items():
        if formattedInput == value:
          return key
    except Exception:
      pass

    raise Exception('Invalid input "{0}"'.format(name))


class TLP_Level(object):
  __tlp_levels = {0 : 'Red',
                1 : 'Amber',
                2 : 'Green',
                3 : 'White'}

  __tlp_colors = {0 : '#FF0000',
                1 : '#FFBF00',
                2 : '#66B032',
                3 : '#F5F5F5'}

  @staticmethod
  def getByID(identifier):
    try:
      identifier = int(identifier)

      if identifier >= 0 and identifier <= 3:
        return TLP_Level.__tlp_levels[identifier]
    except Exception:
      pass

    raise Exception('Invalid input "{0}"'.format(identifier))

  @staticmethod
  def getByName(name):
    try:
      formatedName = str(name).title()

      for key, value in TLP_Level.__tlp_levels.items():
        if formatedName == value:
          return key
    except Exception:
      pass

    raise Exception('Invalid input "{0}"'.format(name))
  
  @staticmethod
  def getColorByID(identifier):
    try:
      identifier = int(identifier)

      if identifier >= 0 and identifier <= 3:
        return TLP_Level.__tlp_colors[identifier]
    except Exception:
      pass

    raise Exception('Invalid input "{0}"'.format(identifier))

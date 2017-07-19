
class Alarm:
    def __init__(self):
        pass

    def fallbackPlan(self, boxes, reason):
        '''What to do if API failed'''
        print "ALARM fallback plan, because " + reason
        # TODO we're offline so check box sizes to determine if we should raise alarm
        self.raiseAlarm()

    def raiseAlarm(self):
        print "ALARM ALERT! ALARM ALERT!"
        # TODO play alarm audio
from activesg import ActiveSG
from credentials import credentials

active_sg = ActiveSG(credentials['username'], credentials['password'])

active_sg.save_list_of_activities()
active_sg.save_list_of_venues()

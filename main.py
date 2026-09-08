import re
import time

import gspread

from spectator import TestDiscraSpectator, DiscraSpectator

# Современный способ авторизации для Service Account
gc = gspread.oauth(credentials_filename='client_secret.json')
spec = DiscraSpectator(gc, 'Профе Дмитрий')
spec.mainloop()
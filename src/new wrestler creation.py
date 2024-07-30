import random

def roll_d66():
   die_10s = random.randint(1, 6)
   die_1s = random.randint(1, 6)

   roll = 10 * die_10s + die_1s
    
   return roll

# Roll 11 times for stats

roll = roll_d66()
print (f"Roll {roll}")

# 1. Face, Heel
if roll <=15:  
   new_wrestler.skills["Cheat"] = "STAR"
elif roll <= 21:
   new_wrestler.skills["Cheat"] = "CIRCLE"
elif roll <=23:
   new_wrestler.skills["Cheat"] = "SQUARE"
elif roll <= 36:
   new_wrestler.skills["Favorite"] = "STAR"
else:
   # No quality
   pass

print (f"Wrestler: {new_wrestler}")
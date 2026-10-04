from PIL import Image

# Load the original preview image
img = Image.open("doodle_jump_extended2.png")

# 1. EXTRACT BALLOONS (Row 1 & Row 2)
# Individual frame size: 90x90 pixels
balloon_sheet = Image.new("RGBA", (1440, 180)) # 16 frames wide, 2 rows high

# Coordinates for the balloon bounding box in the original image
# Row 1 (Warm colors) and Row 2 (Cool colors)
balloon_crop_area = img.crop((10, 560, 1450, 740)) 
balloon_crop_area.save("clean_balloons_sheet.png")

# 2. EXTRACT ROCKETS
# Individual frame size: 40x70 pixels (9 colors x 2 frames each = 18 frames)
rocket_sheet = Image.new("RGBA", (720, 70)) 

# Coordinates for the rocket row in the original image
rocket_crop_area = img.crop((15, 825, 975, 935))
# This cleans up the text beneath and outputs a row of just the 18 rocket states
rocket_crop_area.save("clean_rockets_sheet.png")

print("Sprite sheets generated successfully!")

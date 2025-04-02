from PIL import Image, ImageDraw , ImageFont , ImageEnhance

username = "cosmic"
pfp = "mysteriouscosmic"
# Open images
bannerbasic = Image.open("profileassets/emptybasic.png")
profilepic = Image.open(f"profilegeneration/{pfp}.png").convert("RGBA")
#=-------------------------------- ADDING PFP --------------------------------------------------------

position = (60, 140)
size = (230, 230)

profilepic = profilepic.resize(size)

mask = Image.new("L", size, 0)  # "L" mode for grayscale mask
draw = ImageDraw.Draw(mask)
corner_radius = 20  # Adjust for more/less rounding
draw.rounded_rectangle((0, 0, *size), radius=corner_radius, fill=255)

rounded_pfp = Image.new("RGBA", size, (0, 0, 0, 0))  # Transparent background
rounded_pfp.paste(profilepic, (0, 0), mask)

border_size = 7  # Thickness of the border
border_size_total = size[0] + border_size * 2  # Expand image size

bordered_pfp = Image.new("RGBA", (border_size_total, border_size_total), (255, 255, 255, 255))

border_mask = Image.new("L", (border_size_total, border_size_total), 0)
border_draw = ImageDraw.Draw(border_mask)
border_draw.rounded_rectangle((0, 0, border_size_total, border_size_total), radius=corner_radius + border_size, fill=255)

bordered_pfp.paste(rounded_pfp, (border_size, border_size), rounded_pfp)

final_pfp = Image.new("RGBA", (border_size_total, border_size_total), (0, 0, 0, 0))
final_pfp.paste(bordered_pfp, (0, 0), border_mask)

bannerbasic.paste(final_pfp, (position[0] - border_size, position[1] - border_size), final_pfp)
#-------------------- USER NAME ADDING ----------------------------------
draw = ImageDraw.Draw(bannerbasic)
text = username
text_position = (70, 380)  # Move to a visible position
text_color = (255, 255, 255)  # White color

try:
    font = ImageFont.truetype("profileassets/Evogria.otf", 40)  # Use Arial font with size 40
except IOError:
    font = ImageFont.load_default()  # Fallback to default font
draw.text(text_position, text, font=font, fill=text_color)
#--------------------------------------------------------------------




#------------------------------------- COIN BOX ------------------------------------------


rect = Image.new("RGBA", bannerbasic.size, (255, 255, 255, 0))
draw = ImageDraw.Draw(rect)

x, y = 1150, 80

x0, y0, x1, y1 = 75 + x, 50 + y, 325 + x, 300 + y
radius = 20
fill_color = (255, 255, 255, 200)
border_color = (255, 255, 255, 255)
border_width = 8

draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill_color, outline=border_color, width=border_width)
bannerbasic = Image.alpha_composite(bannerbasic, rect)


#------------------- COIN --------------------------------------------------------------------

dollar = Image.open("profileassets/dollar.png").convert("RGBA")
dollar = dollar.resize((160, 160))
position = (1275, 150)
bannerbasic.paste(dollar, position, dollar)

coin = ImageDraw.Draw(bannerbasic)
coins = 2000000

if coins >= 1000000:
    txt_coin = str(coins/1000000)+"M"
elif coins >= 1000:
    txt_coin = str(coins/1000)+"K"
else:
    txt_coin = str(coin)

coin_font = ImageFont.truetype("profileassets/Evogria.otf", 40)
bbox = coin.textbbox((0, 0), txt_coin, font=coin_font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
text_x = (x0 + x1) // 2 - text_width // 2
text_y = 320

coin.text((text_x, text_y), txt_coin, font=coin_font, fill=(0, 0, 0))

#-------------------- XP BOX-----------------------------------------------

rect2 = Image.new("RGBA", bannerbasic.size, (255, 255, 255, 0))
draw2 = ImageDraw.Draw(rect2)

x2, y2 = 1150, 340

x02, y02, x12, y12 = 75 + x2, 50 + y2, 325 + x2, 180 + y2
radius2 = 20
fill_color2 = (255, 255, 255, 200)
border_color2 = (255, 255, 255, 255)
border_width2 = 8

draw2.rounded_rectangle([x02, y02, x12, y12], radius=radius2, fill=fill_color2, outline=border_color2, width=border_width2)
bannerbasic = Image.alpha_composite(bannerbasic, rect2)

#----------------------------------- XP -----------------------------------------------------
xp_int = 0
xp_str = str(xp_int)

xpimg = Image.open("profileassets/experience.png")
xpimg = xpimg.resize((100, 100))
positionxp = (1220, 405)
bannerbasic.paste(xpimg, positionxp, xpimg)

#-------------------- XP TEXT -------------------------------------------------

xp = ImageDraw.Draw(bannerbasic)

# Format XP display similar to coins
if xp_int >= 1000000:
    xp_text = str(xp_int / 1000000) + "M"
elif xp_int >= 1000:
    xp_text = str(xp_int / 1000) + "K"
else:
    xp_text = str(xp_int)

# Use a slightly larger font for XP text
xp_font = ImageFont.truetype("profileassets/Evogria.otf",60)  # Increased font size

# Calculate text size
bbox_xp = xp.textbbox((0, 0), xp_text, font=xp_font)
text_width_xp = bbox_xp[2] - bbox_xp[0]
text_height_xp = bbox_xp[3] - bbox_xp[1]

# Center text inside the XP box
text_x_xp = (x02 + x12) // 2 - text_width_xp // 2 + 30
text_y_xp = (y02 + y12) // 2 - text_height_xp // 2 - 16  # Adjusted for better centering

# Draw XP text
xp.text((text_x_xp, text_y_xp), xp_text, font=xp_font, fill=(0, 0, 0))




#------------------------- VC BOX --------------------------------------------------------

# Function to add an image in the center of a rectangle
def add_centered_image(base, image_path, rect, size, opacity):
    img = Image.open(image_path).convert("RGBA").resize(size, Image.Resampling.LANCZOS)
    alpha = ImageEnhance.Brightness(img.split()[3]).enhance(opacity / 255.0)
    #img.putalpha(alpha)
    img_x = rect[0] + (rect[2] - rect[0] - size[0]) // 2
    img_y = rect[1] + 20  # Move image slightly down

    if image_path == "profileassets/monitor.png":
        yoff = -45
        xoff = 0
    elif image_path == "profileassets/webcam.png":
        yoff = -50
        xoff = 10
    else:
        yoff = -45
        xoff = 0
    base.paste(img, (img_x+xoff, img_y+yoff), img)

# Function to add two lines of centered text (Number + "HOURS")
def add_centered_text(draw, text, subtext, rect, font_path, font_size, sub_font_size, color):
    font = ImageFont.truetype(font_path, font_size)
    sub_font = ImageFont.truetype(font_path, sub_font_size)
    
    # Calculate text size
    text_w, text_h = draw.textbbox((0, 0), text, font=font)[2:]
    subtext_w, subtext_h = draw.textbbox((0, 0), subtext, font=sub_font)[2:]

    # Center the main text inside the box
    text_x = rect[0] + (rect[2] - rect[0] - text_w) // 2
    text_y = rect[1] + (rect[3] - rect[1]) // 2 - text_h // 2 + 10  # Move up slightly

    # Center the subtext ("HOURS") below the main text
    subtext_x = rect[0] + (rect[2] - rect[0] - subtext_w) // 2
    subtext_y = text_y + text_h + 5  # Small gap between the text and "HOURS"

    draw.text((text_x, text_y), text, font=font, fill=color)
    draw.text((subtext_x, subtext_y), subtext, font=sub_font, fill=color)

# Configuration
div = 20
font_path = "profileassets/digital-7.ttf"
font_size = 60  # Main number size
sub_font_size = 30  # "HOURS" size
fill_color = (255, 255, 255, 0)
border_color = (255, 255, 255, 0)
border_width = 8
radius = 20

# Individual Text Variables
text1, text2, text3 = "1", "8", "69"
subtext = "HOURS"

# Rect3 - Mic Icon
rect3 = Image.new("RGBA", bannerbasic.size, (255, 255, 255, 0))
draw3 = ImageDraw.Draw(rect3)
x3, y3 = 240 + div, 190
x03, y03, x13, y13 = 75 + x3, 50 + y3, 325 + x3, 180 + y3
draw3.rounded_rectangle([x03, y03, x13, y13], radius=radius, fill=fill_color, outline=border_color, width=border_width)
add_centered_image(rect3, "profileassets/mic.png", (x03, y03, x13, y13), size=(65, 65), opacity=100)
add_centered_text(draw3, text1, subtext, (x03, y03, x13, y13), font_path, font_size, sub_font_size, "black")
bannerbasic = Image.alpha_composite(bannerbasic, rect3)

# Rect4 - Webcam Icon
rect4 = Image.new("RGBA", bannerbasic.size, (255, 255, 255, 0))
draw4 = ImageDraw.Draw(rect4)
x4, y4 = 540 + div, 190
x04, y04, x14, y14 = 75 + x4, 50 + y4, 325 + x4, 180 + y4
draw4.rounded_rectangle([x04, y04, x14, y14], radius=radius, fill=fill_color, outline=border_color, width=border_width)
add_centered_image(rect4, "profileassets/webcam.png", (x04, y04, x14, y14), size=(90, 90), opacity=100)
add_centered_text(draw4, text2, subtext, (x04, y04, x14, y14), font_path, font_size, sub_font_size, "black")
bannerbasic = Image.alpha_composite(bannerbasic, rect4)

# Rect5 - Smart TV Icon
rect5 = Image.new("RGBA", bannerbasic.size, (255, 255, 255, 0))
draw5 = ImageDraw.Draw(rect5)
x5, y5 = 840 + div, 190
x05, y05, x15, y15 = 75 + x5, 50 + y5, 325 + x5, 180 + y5
draw5.rounded_rectangle([x05, y05, x15, y15], radius=radius, fill=fill_color, outline=border_color, width=border_width)
add_centered_image(rect5, "profileassets/monitor.png", (x05, y05, x15, y15), size=(70, 70), opacity=100)
add_centered_text(draw5, text3, subtext, (x05, y05, x15, y15), font_path, font_size, sub_font_size, "black")
bannerbasic = Image.alpha_composite(bannerbasic, rect5)

#------------------------------------- STREAK ---------------------------------------------------------
streak = True
days = "23"

white = (255, 255, 255, 255)
orange = (255,140,0,255)

if streak:
    fontfill = orange
    bonfire = Image.open("profileassets/bonfire.png")
else:
    fontfill = white
    bonfire = Image.open("profileassets/extinguishfire.png")

bonfire_x, bonfire_y = 60, 445
bonfire_width, bonfire_height = 90, 90
bonfire = bonfire.resize((bonfire_width, bonfire_height))
bonfire_layer = Image.new("RGBA", bannerbasic.size, (255, 255, 255, 0))
bonfire_layer.paste(bonfire, (bonfire_x, bonfire_y), bonfire)
bannerbasic = Image.alpha_composite(bannerbasic, bonfire_layer)

stats = ImageDraw.Draw(bannerbasic)
font = ImageFont.truetype("profileassets/digital-7.ttf", 90)
text_x, text_y = 170, 450  # Set position
stats.text((text_x, text_y), f"{days}", font=font, fill=fontfill)


#----------- BAR --------------------------------------------------
progress_value = 75  

draw = ImageDraw.Draw(bannerbasic)

progress_value = 75
bar_x, bar_y, bar_width, bar_height = 350, 500, 800, 20
progress_width = int((progress_value / 100) * bar_width)
corner_radius = bar_height // 2  

font = ImageFont.truetype("profileassets/Evogria.otf", 50)  
text = "FAILURE"
text_x, text_y = bar_x, bar_y - 70  

draw.text((text_x, text_y), text, fill="white", font=font)
draw.rounded_rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height], fill=None, outline="white", radius=corner_radius, width=3)
draw.rounded_rectangle([bar_x, bar_y, bar_x + progress_width, bar_y + bar_height], fill="white", radius=corner_radius)












bannerbasic.show()
#outputpath = f"profilegeneration/{pfp}banner.png"
#bannerbasic.save(outputpath)
"""
symbols.py
----------
40 icon symbols for PicToBrix, one per palette color.
Each function draws a simplified vector silhouette.
Signature: s_name(canvas, cx, cy, r)
"""
from __future__ import annotations
import math


# 0 - Calabaza (Pumpkin): round body with ribs + stem + leaf
def s_pumpkin(c, cx, cy, r):
    c.ellipse(cx - r*.82, cy - r*.65, cx + r*.82, cy + r*.42, stroke=0, fill=1)
    c.setLineWidth(max(.4, r*.12))
    c.line(cx - r*.3, cy - r*.55, cx - r*.25, cy + r*.32)
    c.line(cx + r*.3, cy - r*.55, cx + r*.25, cy + r*.32)
    c.line(cx, cy - r*.62, cx, cy + r*.38)
    c.line(cx - r*.05, cy + r*.38, cx + r*.1, cy + r*.65)
    p = c.beginPath()
    p.moveTo(cx + r*.1, cy + r*.6)
    p.lineTo(cx + r*.3, cy + r*.75)
    p.lineTo(cx + r*.15, cy + r*.55)
    c.drawPath(p, stroke=0, fill=1)


# 1 - Paraguas (Umbrella): dome with scalloped bottom + stick + hook
def s_umbrella(c, cx, cy, r):
    p = c.beginPath()
    p.moveTo(cx - r*.88, cy + r*.05)
    p.curveTo(cx - r*.88, cy + r*.92, cx + r*.88, cy + r*.92, cx + r*.88, cy + r*.05)
    p.curveTo(cx + r*.6, cy + r*.2, cx + r*.3, cy + r*.05, cx, cy + r*.2)
    p.curveTo(cx - r*.3, cy + r*.05, cx - r*.6, cy + r*.2, cx - r*.88, cy + r*.05)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.circle(cx, cy + r*.88, r*.06, stroke=0, fill=1)
    c.setLineWidth(max(.4, r*.12))
    c.line(cx, cy + r*.05, cx, cy - r*.62)
    p2 = c.beginPath()
    p2.moveTo(cx, cy - r*.62)
    p2.curveTo(cx - r*.22, cy - r*.82, cx - r*.32, cy - r*.55, cx - r*.15, cy - r*.48)
    c.drawPath(p2, stroke=1, fill=0)


# 2 - Pina (Pineapple): oval with crosshatch + leaf crown
def s_pineapple(c, cx, cy, r):
    c.ellipse(cx - r*.55, cy - r*.78, cx + r*.55, cy + r*.28, stroke=0, fill=1)
    p = c.beginPath()
    p.moveTo(cx - r*.15, cy + r*.28)
    p.curveTo(cx - r*.35, cy + r*.7, cx - r*.1, cy + r*.85, cx, cy + r*.65)
    p.curveTo(cx + r*.1, cy + r*.85, cx + r*.35, cy + r*.7, cx + r*.15, cy + r*.28)
    p.close()
    c.drawPath(p, stroke=0, fill=1)


# 3 - Pato (Duck): round body + head circle + beak
def s_duck(c, cx, cy, r):
    c.ellipse(cx - r*.78, cy - r*.55, cx + r*.3, cy + r*.2, stroke=0, fill=1)
    c.circle(cx + r*.2, cy + r*.38, r*.3, stroke=0, fill=1)
    p = c.beginPath()
    p.moveTo(cx + r*.46, cy + r*.42)
    p.lineTo(cx + r*.85, cy + r*.35)
    p.lineTo(cx + r*.46, cy + r*.3)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    p2 = c.beginPath()
    p2.moveTo(cx - r*.55, cy + r*.15)
    p2.lineTo(cx - r*.78, cy + r*.35)
    p2.lineTo(cx - r*.45, cy + r*.1)
    c.drawPath(p2, stroke=0, fill=1)


# 4 - Foco (Lightbulb): bulb circle + tapered base + lines
def s_lightbulb(c, cx, cy, r):
    c.circle(cx, cy + r*.18, r*.52, stroke=0, fill=1)
    p = c.beginPath()
    p.moveTo(cx - r*.38, cy - r*.12)
    p.lineTo(cx - r*.22, cy - r*.58)
    p.lineTo(cx + r*.22, cy - r*.58)
    p.lineTo(cx + r*.38, cy - r*.12)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.setLineWidth(max(.4, r*.1))
    c.line(cx - r*.24, cy - r*.65, cx + r*.24, cy - r*.65)
    c.line(cx - r*.2, cy - r*.74, cx + r*.2, cy - r*.74)
    c.line(cx - r*.14, cy - r*.82, cx + r*.14, cy - r*.82)


# 5 - Sobre (Envelope): rectangle + V flap
def s_envelope(c, cx, cy, r):
    c.setLineWidth(max(.5, r*.16))
    c.rect(cx - r*.82, cy - r*.48, r*1.64, r*.92, stroke=1, fill=0)
    c.line(cx - r*.82, cy + r*.44, cx, cy - r*.02)
    c.line(cx + r*.82, cy + r*.44, cx, cy - r*.02)
    c.line(cx - r*.82, cy - r*.48, cx - r*.3, cy)
    c.line(cx + r*.82, cy - r*.48, cx + r*.3, cy)


# 6 - Fresa (Strawberry): heart/drop shape + leaf stems + dots
def s_strawberry(c, cx, cy, r):
    p = c.beginPath()
    p.moveTo(cx, cy - r*.82)
    p.curveTo(cx + r*.9, cy + r*.05, cx + r*.55, cy + r*.65, cx, cy + r*.42)
    p.curveTo(cx - r*.55, cy + r*.65, cx - r*.9, cy + r*.05, cx, cy - r*.82)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    p2 = c.beginPath()
    p2.moveTo(cx - r*.2, cy + r*.42)
    p2.lineTo(cx - r*.35, cy + r*.72)
    p2.lineTo(cx - r*.05, cy + r*.52)
    p2.close()
    c.drawPath(p2, stroke=0, fill=1)
    p3 = c.beginPath()
    p3.moveTo(cx + r*.2, cy + r*.42)
    p3.lineTo(cx + r*.35, cy + r*.72)
    p3.lineTo(cx + r*.05, cy + r*.52)
    p3.close()
    c.drawPath(p3, stroke=0, fill=1)


# 7 - Nota musical (Music note): two note heads + stems + beam
def s_music(c, cx, cy, r):
    c.ellipse(cx - r*.62, cy - r*.55, cx - r*.15, cy - r*.25, stroke=0, fill=1)
    c.ellipse(cx + r*.15, cy - r*.65, cx + r*.62, cy - r*.35, stroke=0, fill=1)
    c.setLineWidth(max(.5, r*.13))
    c.line(cx - r*.18, cy - r*.32, cx - r*.18, cy + r*.6)
    c.line(cx + r*.58, cy - r*.42, cx + r*.58, cy + r*.5)
    c.setLineWidth(max(.7, r*.22))
    c.line(cx - r*.18, cy + r*.6, cx + r*.58, cy + r*.5)


# 8 - Regalo (Gift): box + ribbon cross + bow on top
def s_gift(c, cx, cy, r):
    c.setLineWidth(max(.5, r*.14))
    c.rect(cx - r*.68, cy - r*.62, r*1.36, r*.72, stroke=1, fill=0)
    c.rect(cx - r*.72, cy + r*.1, r*1.44, r*.32, stroke=1, fill=0)
    c.line(cx, cy - r*.62, cx, cy + r*.42)
    p = c.beginPath()
    p.moveTo(cx - r*.18, cy + r*.42)
    p.curveTo(cx - r*.38, cy + r*.72, cx - r*.08, cy + r*.72, cx, cy + r*.52)
    p.curveTo(cx + r*.08, cy + r*.72, cx + r*.38, cy + r*.72, cx + r*.18, cy + r*.42)
    c.drawPath(p, stroke=0, fill=1)


# 9 - Camara (Camera): body + lens + flash
def s_camera(c, cx, cy, r):
    c.setLineWidth(max(.5, r*.14))
    rr = r * .08
    c.roundRect(cx - r*.82, cy - r*.42, r*1.64, r*.82, rr, stroke=1, fill=0)
    c.circle(cx + r*.05, cy - r*.05, r*.3, stroke=1, fill=0)
    c.circle(cx + r*.05, cy - r*.05, r*.12, stroke=0, fill=1)
    c.rect(cx + r*.15, cy + r*.4, r*.28, r*.2, stroke=0, fill=1)
    c.rect(cx - r*.55, cy + r*.08, r*.22, r*.12, stroke=0, fill=1)


# 10 - Diamante (Diamond): faceted gem shape
def s_diamond(c, cx, cy, r):
    p = c.beginPath()
    p.moveTo(cx, cy + r*.78)
    p.lineTo(cx + r*.72, cy + r*.2)
    p.lineTo(cx + r*.48, cy - r*.78)
    p.lineTo(cx - r*.48, cy - r*.78)
    p.lineTo(cx - r*.72, cy + r*.2)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.setLineWidth(max(.3, r*.08))
    c.line(cx - r*.72, cy + r*.2, cx + r*.72, cy + r*.2)
    c.line(cx - r*.2, cy + r*.2, cx - r*.35, cy - r*.78)
    c.line(cx + r*.2, cy + r*.2, cx + r*.35, cy - r*.78)
    c.line(cx - r*.2, cy + r*.2, cx, cy + r*.78)
    c.line(cx + r*.2, cy + r*.2, cx, cy + r*.78)


# 11 - Uvas (Grapes): 7 circles in pyramid + 2 leaves
def s_grapes(c, cx, cy, r):
    rr = r * .2
    c.circle(cx - r*.22, cy + r*.12, rr, stroke=0, fill=1)
    c.circle(cx + r*.22, cy + r*.12, rr, stroke=0, fill=1)
    c.circle(cx - r*.22, cy - r*.22, rr, stroke=0, fill=1)
    c.circle(cx + r*.22, cy - r*.22, rr, stroke=0, fill=1)
    c.circle(cx, cy + r*.38, rr, stroke=0, fill=1)
    c.circle(cx, cy + r*.05, rr, stroke=0, fill=1)
    c.circle(cx, cy - r*.52, rr, stroke=0, fill=1)
    p = c.beginPath()
    p.moveTo(cx - r*.05, cy + r*.55)
    p.curveTo(cx - r*.35, cy + r*.82, cx - r*.12, cy + r*.85, cx - r*.05, cy + r*.65)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    p2 = c.beginPath()
    p2.moveTo(cx + r*.05, cy + r*.55)
    p2.curveTo(cx + r*.35, cy + r*.82, cx + r*.12, cy + r*.85, cx + r*.05, cy + r*.65)
    p2.close()
    c.drawPath(p2, stroke=0, fill=1)


# 12 - Cerezas (Cherries): 2 circles + V stems + leaves
def s_cherries(c, cx, cy, r):
    c.circle(cx - r*.35, cy - r*.38, r*.35, stroke=0, fill=1)
    c.circle(cx + r*.35, cy - r*.48, r*.35, stroke=0, fill=1)
    c.setLineWidth(max(.4, r*.12))
    c.line(cx - r*.15, cy - r*.05, cx + r*.05, cy + r*.55)
    c.line(cx + r*.15, cy - r*.15, cx + r*.05, cy + r*.55)
    p = c.beginPath()
    p.moveTo(cx + r*.05, cy + r*.55)
    p.curveTo(cx - r*.15, cy + r*.82, cx + r*.05, cy + r*.82, cx + r*.2, cy + r*.65)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    p2 = c.beginPath()
    p2.moveTo(cx + r*.05, cy + r*.55)
    p2.curveTo(cx + r*.25, cy + r*.82, cx + r*.4, cy + r*.72, cx + r*.3, cy + r*.55)
    p2.close()
    c.drawPath(p2, stroke=0, fill=1)


# 13 - Oso (Bear): face + ears + eyes + snout
def s_bear(c, cx, cy, r):
    c.circle(cx - r*.55, cy + r*.48, r*.25, stroke=0, fill=1)
    c.circle(cx + r*.55, cy + r*.48, r*.25, stroke=0, fill=1)
    c.circle(cx, cy - r*.05, r*.62, stroke=0, fill=1)


# 14 - Trofeo (Trophy): cup + handles + base
def s_trophy(c, cx, cy, r):
    p = c.beginPath()
    p.moveTo(cx - r*.55, cy + r*.62)
    p.lineTo(cx + r*.55, cy + r*.62)
    p.lineTo(cx + r*.4, cy - r*.08)
    p.curveTo(cx + r*.3, cy - r*.5, cx - r*.3, cy - r*.5, cx - r*.4, cy - r*.08)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.setLineWidth(max(.4, r*.1))
    p2 = c.beginPath()
    p2.moveTo(cx - r*.55, cy + r*.45)
    p2.curveTo(cx - r*.82, cy + r*.35, cx - r*.78, cy + r*.05, cx - r*.45, cy + r*.05)
    c.drawPath(p2, stroke=1, fill=0)
    p3 = c.beginPath()
    p3.moveTo(cx + r*.55, cy + r*.45)
    p3.curveTo(cx + r*.82, cy + r*.35, cx + r*.78, cy + r*.05, cx + r*.45, cy + r*.05)
    c.drawPath(p3, stroke=1, fill=0)
    c.line(cx, cy - r*.5, cx, cy - r*.65)
    c.line(cx - r*.25, cy - r*.65, cx + r*.25, cy - r*.65)
    p4 = c.beginPath()
    p4.moveTo(cx - r*.32, cy - r*.78)
    p4.lineTo(cx, cy - r*.65)
    p4.lineTo(cx + r*.32, cy - r*.78)
    p4.close()
    c.drawPath(p4, stroke=0, fill=1)


# 15 - Rayo (Lightning bolt)
def s_lightning(c, cx, cy, r):
    p = c.beginPath()
    p.moveTo(cx + r*.12, cy + r*.82)
    p.lineTo(cx + r*.5, cy + r*.08)
    p.lineTo(cx + r*.05, cy + r*.08)
    p.lineTo(cx - r*.12, cy - r*.82)
    p.lineTo(cx - r*.5, cy - r*.08)
    p.lineTo(cx - r*.05, cy - r*.08)
    p.close()
    c.drawPath(p, stroke=0, fill=1)


# 16 - Ventilador (Fan): circle + 3 curved blades + stand
def s_fan(c, cx, cy, r):
    cy0 = cy + r*.1
    c.setLineWidth(max(.5, r*.12))
    c.circle(cx, cy0, r*.55, stroke=1, fill=0)
    c.circle(cx, cy0, r*.06, stroke=0, fill=1)
    for i in range(3):
        a = math.radians(90 + 120*i)
        bx = cx + r*.3 * math.cos(a)
        by = cy0 + r*.3 * math.sin(a)
        p = c.beginPath()
        p.moveTo(cx, cy0)
        a1 = math.radians(90 + 120*i - 25)
        a2 = math.radians(90 + 120*i + 25)
        p.lineTo(cx + r*.48*math.cos(a1), cy0 + r*.48*math.sin(a1))
        p.curveTo(bx + r*.15*math.cos(a), by + r*.15*math.sin(a),
                  bx + r*.15*math.cos(a), by + r*.15*math.sin(a),
                  cx + r*.48*math.cos(a2), cy0 + r*.48*math.sin(a2))
        p.close()
        c.drawPath(p, stroke=0, fill=1)
    c.line(cx, cy - r*.45, cx, cy - r*.75)
    c.line(cx - r*.25, cy - r*.75, cx + r*.25, cy - r*.75)


# 17 - Bicicleta (Bicycle): 2 wheels + frame
def s_bicycle(c, cx, cy, r):
    c.setLineWidth(max(.5, r*.12))
    c.circle(cx - r*.48, cy - r*.22, r*.35, stroke=1, fill=0)
    c.circle(cx + r*.48, cy - r*.22, r*.35, stroke=1, fill=0)
    c.line(cx - r*.48, cy - r*.22, cx - r*.1, cy + r*.22)
    c.line(cx - r*.1, cy + r*.22, cx + r*.48, cy - r*.22)
    c.line(cx - r*.1, cy + r*.22, cx + r*.2, cy + r*.22)
    c.line(cx + r*.2, cy + r*.22, cx + r*.48, cy - r*.22)
    c.line(cx + r*.15, cy + r*.32, cx + r*.4, cy + r*.32)
    c.rect(cx + r*.25, cy + r*.35, r*.12, r*.12, stroke=0, fill=1)


# 18 - Lampara (Genie lamp): body + dome + spout + smoke spiral
def s_lamp(c, cx, cy, r):
    p = c.beginPath()
    p.moveTo(cx - r*.35, cy - r*.35)
    p.lineTo(cx - r*.2, cy - r*.45)
    p.lineTo(cx + r*.2, cy - r*.45)
    p.lineTo(cx + r*.35, cy - r*.35)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    p2 = c.beginPath()
    p2.moveTo(cx - r*.45, cy - r*.35)
    p2.curveTo(cx - r*.55, cy + r*.15, cx - r*.2, cy + r*.35, cx, cy + r*.2)
    p2.lineTo(cx + r*.5, cy + r*.1)
    p2.lineTo(cx + r*.8, cy - r*.05)
    p2.lineTo(cx + r*.4, cy - r*.15)
    p2.curveTo(cx + r*.2, cy - r*.35, cx - r*.3, cy - r*.4, cx - r*.45, cy - r*.35)
    p2.close()
    c.drawPath(p2, stroke=0, fill=1)
    p3 = c.beginPath()
    p3.moveTo(cx - r*.1, cy + r*.35)
    p3.curveTo(cx - r*.15, cy + r*.55, cx + r*.15, cy + r*.55, cx + r*.1, cy + r*.35)
    p3.close()
    c.drawPath(p3, stroke=0, fill=1)
    c.circle(cx, cy + r*.55, r*.06, stroke=0, fill=1)
    c.setLineWidth(max(.3, r*.08))
    p4 = c.beginPath()
    p4.moveTo(cx - r*.5, cy)
    p4.curveTo(cx - r*.75, cy + r*.15, cx - r*.68, cy + r*.4, cx - r*.5, cy + r*.3)
    p4.curveTo(cx - r*.35, cy + r*.2, cx - r*.45, cy + r*.45, cx - r*.6, cy + r*.35)
    c.drawPath(p4, stroke=1, fill=0)


# 19 - Camion (Truck): cargo box + cab + wheels
def s_truck(c, cx, cy, r):
    c.rect(cx - r*.85, cy - r*.15, r*1.05, r*.65, stroke=0, fill=1)
    p = c.beginPath()
    p.moveTo(cx + r*.2, cy - r*.15)
    p.lineTo(cx + r*.2, cy + r*.5)
    p.lineTo(cx + r*.5, cy + r*.6)
    p.lineTo(cx + r*.8, cy + r*.6)
    p.lineTo(cx + r*.8, cy - r*.15)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    rr = r * .14
    c.circle(cx - r*.52, cy - r*.32, rr, stroke=0, fill=1)
    c.circle(cx - r*.18, cy - r*.32, rr, stroke=0, fill=1)
    c.circle(cx + r*.55, cy - r*.32, rr, stroke=0, fill=1)


# 20 - Platano (Banana): curved crescent
def s_banana(c, cx, cy, r):
    p = c.beginPath()
    p.moveTo(cx + r*.55, cy + r*.6)
    p.curveTo(cx + r*.85, cy + r*.1, cx + r*.35, cy - r*.65, cx - r*.5, cy - r*.55)
    p.curveTo(cx - r*.3, cy - r*.55, cx - r*.2, cy - r*.42, cx - r*.35, cy - r*.35)
    p.curveTo(cx + r*.1, cy - r*.42, cx + r*.55, cy + r*.05, cx + r*.35, cy + r*.5)
    p.close()
    c.drawPath(p, stroke=0, fill=1)


# 21 - Globo aerostatico (Hot air balloon): envelope + basket
def s_balloon(c, cx, cy, r):
    c.circle(cx, cy + r*.2, r*.5, stroke=0, fill=1)
    c.setLineWidth(max(.3, r*.08))
    c.line(cx - r*.32, cy - r*.22, cx - r*.15, cy - r*.68)
    c.line(cx + r*.32, cy - r*.22, cx + r*.15, cy - r*.68)
    c.rect(cx - r*.18, cy - r*.82, r*.36, r*.18, stroke=0, fill=1)
    c.line(cx - r*.45, cy + r*.25, cx + r*.45, cy + r*.25)
    c.line(cx - r*.38, cy + r*.05, cx + r*.38, cy + r*.05)


# 22 - Helicoptero (Helicopter): body + rotor + tail + wheels
def s_helicopter(c, cx, cy, r):
    c.ellipse(cx - r*.55, cy - r*.3, cx + r*.35, cy + r*.22, stroke=0, fill=1)
    p = c.beginPath()
    p.moveTo(cx + r*.35, cy)
    p.lineTo(cx + r*.75, cy + r*.18)
    p.lineTo(cx + r*.8, cy + r*.12)
    p.lineTo(cx + r*.35, cy - r*.08)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.setLineWidth(max(.5, r*.12))
    c.line(cx - r*.82, cy + r*.38, cx + r*.65, cy + r*.38)
    c.line(cx - r*.1, cy + r*.22, cx - r*.1, cy + r*.38)
    rr = r * .07
    c.circle(cx - r*.3, cy - r*.38, rr, stroke=0, fill=1)
    c.circle(cx + r*.05, cy - r*.38, rr, stroke=0, fill=1)


# 23 - Camello (Camel): humped silhouette
def s_camel(c, cx, cy, r):
    p = c.beginPath()
    p.moveTo(cx - r*.65, cy - r*.55)
    p.lineTo(cx - r*.65, cy + r*.05)
    p.curveTo(cx - r*.45, cy + r*.48, cx - r*.12, cy + r*.25, cx + r*.05, cy + r*.48)
    p.curveTo(cx + r*.2, cy + r*.25, cx + r*.35, cy + r*.35, cx + r*.5, cy + r*.2)
    p.lineTo(cx + r*.52, cy + r*.48)
    p.lineTo(cx + r*.62, cy + r*.38)
    p.lineTo(cx + r*.68, cy + r*.5)
    p.lineTo(cx + r*.75, cy - r*.55)
    p.lineTo(cx + r*.58, cy - r*.55)
    p.lineTo(cx + r*.55, cy - r*.15)
    p.lineTo(cx - r*.48, cy - r*.15)
    p.lineTo(cx - r*.48, cy - r*.55)
    p.close()
    c.drawPath(p, stroke=0, fill=1)


# 24 - Carrito (Shopping cart)
def s_cart(c, cx, cy, r):
    c.setLineWidth(max(.5, r*.14))
    p = c.beginPath()
    p.moveTo(cx - r*.78, cy + r*.48)
    p.lineTo(cx - r*.55, cy + r*.15)
    p.lineTo(cx - r*.38, cy - r*.18)
    p.lineTo(cx + r*.55, cy - r*.18)
    p.lineTo(cx + r*.65, cy + r*.32)
    p.lineTo(cx - r*.32, cy + r*.32)
    c.drawPath(p, stroke=1, fill=0)
    rr = r * .12
    c.circle(cx - r*.2, cy - r*.38, rr, stroke=0, fill=1)
    c.circle(cx + r*.4, cy - r*.38, rr, stroke=0, fill=1)


# 25 - Alcancia (Piggy bank): body + ear + coin + legs
def s_piggybank(c, cx, cy, r):
    c.ellipse(cx - r*.7, cy - r*.38, cx + r*.55, cy + r*.35, stroke=0, fill=1)
    p = c.beginPath()
    p.moveTo(cx - r*.5, cy + r*.2)
    p.lineTo(cx - r*.42, cy + r*.48)
    p.lineTo(cx - r*.28, cy + r*.28)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.circle(cx + r*.05, cy + r*.5, r*.15, stroke=0, fill=1)
    c.setLineWidth(max(.3, r*.08))
    c.line(cx - r*.42, cy - r*.38, cx - r*.42, cy - r*.58)
    c.line(cx - r*.12, cy - r*.4, cx - r*.12, cy - r*.58)
    c.line(cx + r*.15, cy - r*.4, cx + r*.15, cy - r*.58)
    c.line(cx + r*.38, cy - r*.38, cx + r*.38, cy - r*.55)
    c.circle(cx - r*.62, cy, r*.04, stroke=0, fill=1)


# 26 - Gota (Water drop)
def s_drop(c, cx, cy, r):
    p = c.beginPath()
    p.moveTo(cx, cy + r*.85)
    p.curveTo(cx + r*.85, cy - r*.1, cx + r*.55, cy - r*.85, cx, cy - r*.85)
    p.curveTo(cx - r*.55, cy - r*.85, cx - r*.85, cy - r*.1, cx, cy + r*.85)
    p.close()
    c.drawPath(p, stroke=0, fill=1)


# 27 - Raton de cuerda (Wind-up mouse)
def s_mouse(c, cx, cy, r):
    p = c.beginPath()
    p.moveTo(cx - r*.65, cy - r*.2)
    p.curveTo(cx - r*.65, cy + r*.48, cx + r*.65, cy + r*.48, cx + r*.65, cy - r*.2)
    p.lineTo(cx - r*.65, cy - r*.2)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.circle(cx + r*.42, cy + r*.32, r*.18, stroke=0, fill=1)
    c.setLineWidth(max(.4, r*.1))
    p2 = c.beginPath()
    p2.moveTo(cx - r*.65, cy - r*.02)
    p2.curveTo(cx - r*.85, cy + r*.15, cx - r*.8, cy + r*.35, cx - r*.6, cy + r*.22)
    c.drawPath(p2, stroke=1, fill=0)
    c.line(cx - r*.08, cy + r*.22, cx - r*.08, cy + r*.52)
    c.circle(cx - r*.18, cy + r*.58, r*.06, stroke=0, fill=1)
    c.circle(cx + r*.02, cy + r*.58, r*.06, stroke=0, fill=1)


# 28 - Sol (Sun): circle + 8 pointed chevron rays
def s_sun(c, cx, cy, r):
    c.circle(cx, cy, r*.38, stroke=0, fill=1)
    c.setLineWidth(max(.5, r*.12))
    for i in range(8):
        a = math.radians(i * 45)
        x1 = cx + r*.5 * math.cos(a)
        y1 = cy + r*.5 * math.sin(a)
        x2 = cx + r*.82 * math.cos(a)
        y2 = cy + r*.82 * math.sin(a)
        perp_x = r*.12 * math.cos(a + math.pi/2)
        perp_y = r*.12 * math.sin(a + math.pi/2)
        p = c.beginPath()
        p.moveTo(x1 + perp_x, y1 + perp_y)
        p.lineTo(x2, y2)
        p.lineTo(x1 - perp_x, y1 - perp_y)
        p.close()
        c.drawPath(p, stroke=0, fill=1)


# 29 - Helado (Ice cream cone): cone + 3 scoops
def s_icecream(c, cx, cy, r):
    p = c.beginPath()
    p.moveTo(cx - r*.35, cy - r*.08)
    p.lineTo(cx, cy - r*.85)
    p.lineTo(cx + r*.35, cy - r*.08)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.circle(cx, cy + r*.25, r*.3, stroke=0, fill=1)
    c.circle(cx - r*.28, cy - r*.02, r*.25, stroke=0, fill=1)
    c.circle(cx + r*.28, cy - r*.02, r*.25, stroke=0, fill=1)


# 30 - Dona (Donut): ring with bite
def s_donut(c, cx, cy, r):
    c.setLineWidth(max(.8, r*.32))
    c.circle(cx, cy, r*.52, stroke=1, fill=0)


# 31 - Mano (Pointing hand)
def s_hand(c, cx, cy, r):
    c.rect(cx - r*.72, cy - r*.32, r*.85, r*.65, stroke=0, fill=1)
    c.setLineWidth(max(.4, r*.1))
    for i in range(4):
        y = cy + r*.18 - i * r*.16
        c.line(cx + r*.13, y, cx + r*.72, y)
    p = c.beginPath()
    p.moveTo(cx - r*.72, cy + r*.33)
    p.curveTo(cx - r*.72, cy + r*.55, cx - r*.5, cy + r*.55, cx - r*.5, cy + r*.33)
    c.drawPath(p, stroke=0, fill=1)


# 32 - Hueso (Bone): dumbbell shape
def s_bone(c, cx, cy, r):
    a = math.radians(35)
    dx, dy = r*.5*math.cos(a), r*.5*math.sin(a)
    c.setLineWidth(max(.8, r*.28))
    c.line(cx - dx, cy - dy, cx + dx, cy + dy)
    rr = r * .2
    c.circle(cx - dx - rr*.6, cy - dy + rr*.55, rr, stroke=0, fill=1)
    c.circle(cx - dx + rr*.55, cy - dy - rr*.6, rr, stroke=0, fill=1)
    c.circle(cx + dx + rr*.6, cy + dy - rr*.55, rr, stroke=0, fill=1)
    c.circle(cx + dx - rr*.55, cy + dy + rr*.6, rr, stroke=0, fill=1)


# 33 - Reloj (Alarm clock): face + hands + bells + legs
def s_clock(c, cx, cy, r):
    c.setLineWidth(max(.5, r*.12))
    c.circle(cx, cy, r*.55, stroke=1, fill=0)
    c.line(cx, cy, cx, cy + r*.22)
    c.line(cx, cy, cx + r*.22, cy - r*.08)
    p = c.beginPath()
    p.moveTo(cx - r*.35, cy + r*.52)
    p.curveTo(cx - r*.28, cy + r*.72, cx - r*.15, cy + r*.7, cx - r*.18, cy + r*.52)
    c.drawPath(p, stroke=1, fill=0)
    p2 = c.beginPath()
    p2.moveTo(cx + r*.35, cy + r*.52)
    p2.curveTo(cx + r*.28, cy + r*.72, cx + r*.15, cy + r*.7, cx + r*.18, cy + r*.52)
    c.drawPath(p2, stroke=1, fill=0)
    c.line(cx - r*.38, cy - r*.58, cx - r*.55, cy - r*.72)
    c.line(cx + r*.38, cy - r*.58, cx + r*.55, cy - r*.72)


# 34 - Campana (Bell)
def s_bell(c, cx, cy, r):
    p = c.beginPath()
    p.moveTo(cx - r*.6, cy - r*.38)
    p.curveTo(cx - r*.65, cy + r*.15, cx - r*.28, cy + r*.62, cx, cy + r*.62)
    p.curveTo(cx + r*.28, cy + r*.62, cx + r*.65, cy + r*.15, cx + r*.6, cy - r*.38)
    p.lineTo(cx - r*.6, cy - r*.38)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.circle(cx, cy + r*.72, r*.08, stroke=0, fill=1)
    c.circle(cx, cy - r*.5, r*.1, stroke=0, fill=1)


# 35 - Ojo (Eye): almond shape + iris + pupil
def s_eye(c, cx, cy, r):
    p = c.beginPath()
    p.moveTo(cx - r*.88, cy)
    p.curveTo(cx - r*.4, cy + r*.62, cx + r*.4, cy + r*.62, cx + r*.88, cy)
    p.curveTo(cx + r*.4, cy - r*.62, cx - r*.4, cy - r*.62, cx - r*.88, cy)
    p.close()
    c.drawPath(p, stroke=0, fill=1)


# 36 - Pez (Fish): body + tail + eye line
def s_fish(c, cx, cy, r):
    p = c.beginPath()
    p.moveTo(cx + r*.65, cy)
    p.curveTo(cx + r*.3, cy + r*.5, cx - r*.3, cy + r*.42, cx - r*.42, cy)
    p.curveTo(cx - r*.3, cy - r*.42, cx + r*.3, cy - r*.5, cx + r*.65, cy)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    p2 = c.beginPath()
    p2.moveTo(cx - r*.42, cy)
    p2.lineTo(cx - r*.78, cy + r*.35)
    p2.lineTo(cx - r*.78, cy - r*.35)
    p2.close()
    c.drawPath(p2, stroke=0, fill=1)


# 37 - Balanza (Scale): post + beam + pans
def s_scale(c, cx, cy, r):
    c.setLineWidth(max(.5, r*.14))
    c.line(cx, cy - r*.72, cx, cy + r*.52)
    c.line(cx - r*.65, cy + r*.28, cx + r*.65, cy + r*.45)
    c.line(cx - r*.35, cy - r*.72, cx + r*.35, cy - r*.72)
    p1 = c.beginPath()
    p1.moveTo(cx - r*.8, cy - r*.02)
    p1.lineTo(cx - r*.65, cy + r*.28)
    p1.lineTo(cx - r*.5, cy - r*.02)
    p1.close()
    c.drawPath(p1, stroke=0, fill=1)
    p2 = c.beginPath()
    p2.moveTo(cx + r*.5, cy + r*.15)
    p2.lineTo(cx + r*.65, cy + r*.45)
    p2.lineTo(cx + r*.8, cy + r*.15)
    p2.close()
    c.drawPath(p2, stroke=0, fill=1)


# 38 - Avion (Airplane): cross shape
def s_airplane(c, cx, cy, r):
    p = c.beginPath()
    p.moveTo(cx, cy + r*.85)
    p.lineTo(cx + r*.12, cy + r*.25)
    p.lineTo(cx + r*.82, cy + r*.08)
    p.lineTo(cx + r*.82, cy - r*.08)
    p.lineTo(cx + r*.12, cy - r*.02)
    p.lineTo(cx + r*.1, cy - r*.42)
    p.lineTo(cx + r*.4, cy - r*.52)
    p.lineTo(cx + r*.4, cy - r*.65)
    p.lineTo(cx, cy - r*.52)
    p.lineTo(cx - r*.4, cy - r*.65)
    p.lineTo(cx - r*.4, cy - r*.52)
    p.lineTo(cx - r*.1, cy - r*.42)
    p.lineTo(cx - r*.12, cy - r*.02)
    p.lineTo(cx - r*.82, cy - r*.08)
    p.lineTo(cx - r*.82, cy + r*.08)
    p.lineTo(cx - r*.12, cy + r*.25)
    p.close()
    c.drawPath(p, stroke=0, fill=1)


# 39 - Aguacate (Avocado): outer oval + inner pit
def s_avocado(c, cx, cy, r):
    p = c.beginPath()
    p.moveTo(cx, cy + r*.82)
    p.curveTo(cx + r*.62, cy + r*.52, cx + r*.68, cy - r*.18, cx + r*.42, cy - r*.62)
    p.curveTo(cx + r*.18, cy - r*.88, cx - r*.18, cy - r*.88, cx - r*.42, cy - r*.62)
    p.curveTo(cx - r*.68, cy - r*.18, cx - r*.62, cy + r*.52, cx, cy + r*.82)
    p.close()
    c.drawPath(p, stroke=0, fill=1)


SYMBOLS = [
    s_pumpkin, s_umbrella, s_pineapple, s_duck, s_lightbulb,
    s_envelope, s_strawberry, s_music, s_gift, s_camera,
    s_diamond, s_grapes, s_cherries, s_bear, s_trophy,
    s_lightning, s_fan, s_bicycle, s_lamp, s_truck,
    s_banana, s_balloon, s_helicopter, s_camel, s_cart,
    s_piggybank, s_drop, s_mouse, s_sun, s_icecream,
    s_donut, s_hand, s_bone, s_clock, s_bell,
    s_eye, s_fish, s_scale, s_airplane, s_avocado,
]

_FALLBACK_CHARS = "ABCDEFGHJKLMNPRSTUVWXYZ23456789"


def assign_symbols(n: int) -> list:
    out = []
    for i in range(n):
        if i < len(SYMBOLS):
            out.append(_wrap(SYMBOLS[i]))
        else:
            ch = _FALLBACK_CHARS[(i - len(SYMBOLS)) % len(_FALLBACK_CHARS)]
            out.append(_make_char(ch))
    return out


def _wrap(fn):
    def draw(c, cx, cy, r, ink):
        c.saveState()
        c.setStrokeColor(ink)
        c.setFillColor(ink)
        fn(c, cx, cy, r)
        c.restoreState()
    return draw


def _make_char(ch):
    def draw(c, cx, cy, r, ink):
        c.saveState()
        c.setFillColor(ink)
        fs = r * 1.7
        c.setFont("Helvetica-Bold", fs)
        c.drawCentredString(cx, cy - fs * 0.36, ch)
        c.restoreState()
    return draw

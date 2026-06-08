"""
build_ability_mechanics.py

Constructs data/ability_mechanics.json — a structured catalog of every star
power, gadget, and hypercharge in Brawl Stars (v67.301).

Strategy:
  1. Source of "what the wiki says" per ability is kits.json (pre-fetched).
  2. Each ability is joined to its CSV row via cards.csv (Target = internalName,
     MetaType = 4/5/6).
  3. Gadgets (MetaType=5) link to accessories.csv via Skill column.
  4. Star powers (MetaType=4) describe themselves via Type, StatusEffect,
     AreaEffect, Traits, Projectiles columns.
  5. Hypercharges (MetaType=6) baseline = default speed/damage/shield buff;
     unique modifiers come from the Type tag (overcharge_<brawler>) which is
     researched per-brawler from the wiki text.
  6. We use the wiki prose as primary source for mechanic identification, then
     verify against CSV. csvVerified="true" if the CSV row corroborates the
     described mechanic, "partial" if the CSV row exists but doesn't directly
     confirm the precise mechanic, "wiki-only" if no CSV row, "csv-disagrees"
     if CSV contradicts.
"""

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
CSV_DIR = ROOT / "csv_logic"

# -----------------------------------------------------------------------------
# Load all source CSVs into name-keyed dicts.
# -----------------------------------------------------------------------------


def load_csv(name):
    path = CSV_DIR / name
    with path.open() as f:
        r = csv.DictReader(f)
        rows = list(r)
    # First row is type signature line
    if rows and rows[0].get("Name") == "string":
        rows = rows[1:]
    return rows


def by_name(rows):
    return {r["Name"]: r for r in rows if r.get("Name")}


cards = load_csv("cards.csv")
accessories = by_name(load_csv("accessories.csv"))
skills = by_name(load_csv("skills.csv"))
projectiles = by_name(load_csv("projectiles_logic.csv"))
traits = by_name(load_csv("traits.csv"))
area_effects = by_name(load_csv("area_effects.csv"))
characters = by_name(load_csv("characters.csv"))


# -----------------------------------------------------------------------------
# Load kits.json (wiki summaries) and brawlers.json (display names).
# -----------------------------------------------------------------------------

with (ROOT / "kits.json").open() as f:
    kits_data = json.load(f)["kits"]

with (ROOT / "brawlers.json").open() as f:
    brawlers_data = json.load(f)["brawlers"]


# Build internal name -> display name from brawlers.json
internal_to_display = {b["internalName"]: b["name"] for b in brawlers_data if b.get("internalName")}
# Also map by display
display_to_internal = {b["name"]: b["internalName"] for b in brawlers_data if b.get("internalName")}
# kits-only Buzz Lightyear -> internal "Lightyear"
display_to_internal.setdefault("Buzz Lightyear", "Lightyear")
internal_to_display.setdefault("Lightyear", "Buzz Lightyear")

# slugged-name (from kits dict key) -> internal name. Many kits keys differ from internal.
# We'll look it up by display name (kits[k]["name"]).
display_to_kits_entry = {kits_data[k]["name"]: kits_data[k] for k in kits_data}


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------


def i_or_none(v):
    if v is None:
        return None
    v = str(v).strip()
    if not v:
        return None
    try:
        return int(v)
    except ValueError:
        try:
            return float(v)
        except ValueError:
            return None


def to_tiles(v):
    """Convert raw projectile/area radius/range from 480-units-per-tile to tiles."""
    n = i_or_none(v)
    if n is None:
        return None
    return round(n / 480.0, 2)


def cooldown_to_sec(v):
    """Accessories Cooldown is in deciseconds-ish... actually looks like 1/100 sec.
    Quick spot check: ElectroSniper_Bounce Cooldown=280, wiki says ~28 sec? Actually gadgets are
    3 uses per match, no cooldown shown to player. The numeric Cooldown is probably internal.
    For accessories the standard 'gadget uses' are baked elsewhere; we capture it raw and note.
    """
    n = i_or_none(v)
    if n is None:
        return None
    return n  # raw — too uncertain to convert; consumer can interpret


def ticks_to_sec(v):
    """Engine runs at 20 ticks/sec."""
    n = i_or_none(v)
    if n is None:
        return None
    return round(n / 20.0, 2)


def ms_to_sec(v):
    n = i_or_none(v)
    if n is None:
        return None
    return round(n / 1000.0, 3)


def clean_row(row):
    return {k: v for k, v in row.items() if v and str(v).strip()}


# -----------------------------------------------------------------------------
# Star-power mechanic interpretation. We expose a small set of recurring
# heuristics keyed off cards.Type so the auto-extracted record reflects what's
# in the CSV; the prose summary already comes from kits.json.
# -----------------------------------------------------------------------------

# Recurring star-power Type tags and their canonical interpretation. Keys are
# cards.Type values (MetaType=4 rows). Each entry returns extra fields to merge
# into the ability record.
def sp_mechanic_from_type(t, card_row):
    """Auto-fill a few mechanic fields based on the cards.Type tag of a star power.

    Returns a dict of mechanic fields to merge. None values are dropped at write time.
    """
    val = i_or_none(card_row.get("Value"))
    val2 = i_or_none(card_row.get("Value2"))
    val3 = i_or_none(card_row.get("Value3"))
    status = card_row.get("StatusEffect") or None

    out = {}

    if t == "petrol_reload":
        # Reload-bonus star power.
        out["trigger"] = "passive"
        out["statusEffects"] = [
            {"target": "self", "effect": "reload-buff", "magnitude": val, "durationSec": None}
        ]
    elif t == "trait_star_power":
        # The 'Traits' column holds the modifier name; effect varies.
        out["trigger"] = "passive"
    elif t == "aoe_dot":
        out["trigger"] = "passive"
        out["statusEffects"] = [
            {"target": "enemy", "effect": "poison", "magnitude": val, "durationSec": None}
        ]
    elif t == "low_health_shield":
        out["trigger"] = "on-low-hp"
        out["statusEffects"] = [
            {"target": "self", "effect": "shield", "magnitude": val, "durationSec": None}
        ]
    elif t == "heal_main_attack" or t == "heal_self_main_attack" or t == "heal_others_main_attack":
        out["trigger"] = "passive"
        target = "ally" if "others" in t else "self"
        out["statusEffects"] = [
            {"target": target, "effect": "heal", "magnitude": val, "durationSec": None}
        ]
    elif t == "heal_invisible":
        out["trigger"] = "passive"
        out["statusEffects"] = [
            {"target": "self", "effect": "heal", "magnitude": val, "durationSec": None},
            {"target": "self", "effect": "invisible", "magnitude": None, "durationSec": None},
        ]
    elif t == "shield_homerun":
        out["trigger"] = "on-super-charged"
        out["statusEffects"] = [
            {"target": "self", "effect": "shield", "magnitude": val, "durationSec": None}
        ]
    elif t == "damage_buff_super" or t == "damage_super":
        out["trigger"] = "passive"
        out["modifiesAbility"] = "super"
    elif t == "fire_dot_ulti":
        out["trigger"] = "on-super-used"
        out["modifiesAbility"] = "super"
        out["statusEffects"] = [
            {"target": "enemy", "effect": "burn", "magnitude": val, "durationSec": None}
        ]
    elif t == "ulti_give_status_effect_enemy":
        out["trigger"] = "passive"
        out["modifiesAbility"] = "super"
        out["statusEffects"] = [
            {"target": "enemy", "effect": "slow", "magnitude": val, "durationSec": ms_to_sec(val2)}
        ]
    elif t == "ulti_area_status" or t == "ulti_spawn_explosion" or t == "ulti_change":
        out["trigger"] = "passive"
        out["modifiesAbility"] = "super"
    elif t == "reload_debuff":
        out["trigger"] = "on-hit"
        out["statusEffects"] = [
            {"target": "enemy", "effect": "silence", "magnitude": None, "durationSec": ms_to_sec(val)}
        ]
    elif t == "speed_invisible":
        out["trigger"] = "passive"
        out["statusEffects"] = [
            {"target": "self", "effect": "invisible", "magnitude": None, "durationSec": None},
            {"target": "self", "effect": "speed-up", "magnitude": val, "durationSec": None},
        ]
    elif t == "alt_character":
        out["trigger"] = "on-super-used"
        out["modifiesAbility"] = "super"
    elif t == "berserker":
        out["trigger"] = "on-low-hp"
    elif t == "more_bullets_ulti":
        out["trigger"] = "passive"
        out["modifiesAbility"] = "super"
        out["projectileMod"] = {"extraProjectiles": val}
    elif t == "bounced_bullets_stronger":
        out["trigger"] = "passive"
        out["modifiesAbility"] = "weapon"
        out["projectileMod"] = {"bouncesOffWalls": True}
    elif t == "stun_wall_push":
        out["trigger"] = "on-hit"
        out["statusEffects"] = [
            {"target": "enemy", "effect": "stun", "magnitude": None, "durationSec": ms_to_sec(val)}
        ]
    elif t == "attack_gives_status_effect":
        out["trigger"] = "on-hit"
        if status:
            out["statusEffects"] = [
                {"target": "enemy", "effect": "applies-" + status, "magnitude": None, "durationSec": None}
            ]
    elif t == "cripple":
        out["trigger"] = "on-hit"
        out["statusEffects"] = [
            {"target": "enemy", "effect": "weakness", "magnitude": val, "durationSec": None}
        ]
    elif t == "attack_range":
        out["trigger"] = "passive"
        out["modifiesAbility"] = "weapon"
        out["rangeMod"] = {"flat": val, "rawCsvValue": val}
    elif t == "projectile_speed":
        out["trigger"] = "passive"
        out["modifiesAbility"] = "weapon"
        out["projectileMod"] = {"speedMultiplier": (val / 100.0) if val else None}
    elif t == "speed_after_ulti" or t == "speed_full_ammo":
        out["trigger"] = "passive"
        out["statusEffects"] = [
            {"target": "self", "effect": "speed-up", "magnitude": val, "durationSec": None}
        ]
    elif t == "speedy" or t == "speed_invisible":
        out["trigger"] = "passive"
    elif t == "consumable_shield":
        out["trigger"] = "passive"
        out["statusEffects"] = [
            {"target": "self", "effect": "shield", "magnitude": val, "durationSec": None}
        ]
    elif t == "medikit":
        out["trigger"] = "active"
        out["statusEffects"] = [
            {"target": "self", "effect": "heal", "magnitude": val, "durationSec": None}
        ]
    elif t == "domain_additional_status":
        out["trigger"] = "passive"
        out["modifiesAbility"] = "super"
    elif t == "barrel_defense":
        out["trigger"] = "on-super-used"
        out["statusEffects"] = [
            {"target": "self", "effect": "shield", "magnitude": val, "durationSec": None}
        ]
    elif t == "ulti_defense":
        out["trigger"] = "on-super-used"
    elif t == "extra_bullet":
        out["trigger"] = "passive"
        out["modifiesAbility"] = "weapon"
        out["projectileMod"] = {"extraProjectiles": val}
    elif t == "chain_spread":
        out["trigger"] = "passive"
        out["modifiesAbility"] = "weapon"
    elif t == "curve_ball":
        out["trigger"] = "passive"
        out["modifiesAbility"] = "weapon"
    elif t == "ambush":
        out["trigger"] = "passive"
    elif t == "spot":
        out["trigger"] = "passive"
    elif t == "ulti_reload_debuff":
        out["trigger"] = "on-super-hit"
        out["modifiesAbility"] = "super"
        out["statusEffects"] = [
            {"target": "enemy", "effect": "silence", "magnitude": None, "durationSec": ms_to_sec(val)}
        ]
    elif t == "electro_shield":
        out["trigger"] = "on-hit"
        out["statusEffects"] = [
            {"target": "self", "effect": "shield", "magnitude": val, "durationSec": ticks_to_sec(val2)}
        ]
    elif t == "stun_trap":
        out["trigger"] = "on-super-used"
        out["statusEffects"] = [
            {"target": "enemy", "effect": "stun", "magnitude": None, "durationSec": ms_to_sec(val)}
        ]
    elif t == "steal_souls" or t == "steal_souls2":
        out["trigger"] = "on-hit"
    elif t == "pet_attack_speed":
        out["trigger"] = "passive"
    elif t == "pet_lifesteal":
        out["trigger"] = "passive"
        out["statusEffects"] = [
            {"target": "self", "effect": "lifesteal", "magnitude": val, "durationSec": None}
        ]
    elif t == "repair_self" or t == "repair_turret":
        out["trigger"] = "passive"
    elif t == "aoe_regenerate" or t == "heal_forest":
        out["trigger"] = "passive"
        out["statusEffects"] = [
            {"target": "ally", "effect": "heal-aura", "magnitude": val, "durationSec": None}
        ]
    elif t == "black_hole_monster":
        out["trigger"] = "on-super-used"
        out["modifiesAbility"] = "super"
    elif t == "pushback_self":
        out["trigger"] = "active"
    elif t == "turret_electricity":
        out["trigger"] = "passive"
    elif t == "prey_on_the_weak":
        out["trigger"] = "passive"
    elif t == "remove_status":
        out["trigger"] = "active"

    return {k: v for k, v in out.items() if v is not None}


# -----------------------------------------------------------------------------
# Gadget mechanic interpretation from accessories.csv row + summary text.
# -----------------------------------------------------------------------------


def gadget_mechanic_from_row(acc_row, summary):
    """Pull structured mechanics from accessories.csv row + wiki summary."""
    if not acc_row:
        return {}

    out = {}
    typ = acc_row.get("Type", "")

    # AreaEffect link — many typeless gadgets (e.g., Rosa GrowBush, Barkeep Slow,
    # Poco Da Capo regen, Mr P Service Bell) reference an area_effects row that
    # has the actual mechanic.
    ae_name = acc_row.get("AreaEffect")
    if ae_name and ae_name in area_effects:
        ae = area_effects[ae_name]
        rad = to_tiles(ae.get("Radius"))
        t_ms = i_or_none(ae.get("TimeMs"))
        ent = {"entity": ae_name, "stationary": True}
        if rad is not None:
            ent["radiusTiles"] = rad
        if t_ms is not None:
            ent["lifetimeSec"] = ms_to_sec(t_ms)
        out["spawnsEntity"] = ent

    # Projectile link via CustomObject — covers next_attack_change gadgets that
    # swap in a modified projectile.
    co_name = acc_row.get("CustomObject")
    if co_name and co_name in projectiles:
        proj = projectiles[co_name]
        pm = {}
        if proj.get("IsBouncing") == "true":
            pm["bouncesOffWalls"] = True
            mdb = i_or_none(proj.get("MaxDistanceBounces"))
            daf = i_or_none(proj.get("DistanceAddFromBounce"))
            if daf:
                pm["bounceExtraTiles"] = round(daf / 480.0, 2)
            if mdb:
                pm["bounceCount"] = mdb
        if proj.get("PiercesCharacters"):
            pm["pierces"] = True
        if proj.get("IsHomingMissile") or proj.get("IsFriendlyHomingMissile"):
            pm["homing"] = True
        spd = i_or_none(proj.get("Speed"))
        if spd:
            pm["speedRaw"] = spd
        rad = i_or_none(proj.get("Radius"))
        if rad:
            pm["projRadiusTiles"] = round(rad / 480.0, 2)
        if pm:
            out["projectileMod"] = pm
    ue = acc_row.get("UseEffect", "")
    cd = i_or_none(acc_row.get("Cooldown"))
    if cd is not None:
        out["_cooldownRaw"] = cd  # raw value; player-facing gadgets are uses-based
    sub_type = i_or_none(acc_row.get("SubType"))
    if sub_type is not None:
        out["uses"] = sub_type  # SubType reliably encodes uses-per-match (1-3)

    sea = acc_row.get("StatusEffectEnemy")
    saa = acc_row.get("StatusEffectAlly")
    sh = i_or_none(acc_row.get("ShieldPercent"))
    sh_ticks = i_or_none(acc_row.get("ShieldTicks"))
    sb = i_or_none(acc_row.get("SpeedBoost"))
    sb_ticks = i_or_none(acc_row.get("SpeedBoostTicks"))
    active_ticks = i_or_none(acc_row.get("ActiveTicks"))
    raw_range = i_or_none(acc_row.get("Range"))

    if raw_range:
        out["rangeRaw"] = raw_range  # in 480-units; consumer can divide

    # Status effects
    fx = []
    if sh and sh_ticks:
        fx.append({"target": "self", "effect": "shield", "magnitude": sh, "durationSec": ticks_to_sec(sh_ticks)})
    if sb and sb_ticks:
        fx.append({"target": "self", "effect": "speed-up", "magnitude": sb, "durationSec": ticks_to_sec(sb_ticks)})
    if sea:
        fx.append({"target": "enemy", "effect": "applies-" + sea, "magnitude": None, "durationSec": None})
    if saa:
        fx.append({"target": "ally", "effect": "applies-" + saa, "magnitude": None, "durationSec": None})
    if fx:
        out["statusEffects"] = fx

    # Trigger
    if typ == "" or typ is None:
        out["trigger"] = "active"
    elif typ == "next_attack_change":
        out["trigger"] = "active"
        out["modifiesAbility"] = "weapon"
        out["duration"] = "until-fired"
    elif typ == "spawn":
        out["trigger"] = "active"
        custom_obj = acc_row.get("CustomObject")
        if custom_obj and "spawnsEntity" not in out:
            ae = area_effects.get(custom_obj)
            if ae:
                ent = {"entity": custom_obj, "stationary": True}
                rad = to_tiles(ae.get("Radius"))
                if rad is not None:
                    ent["radiusTiles"] = rad
                t_ms = i_or_none(ae.get("TimeMs"))
                if t_ms is not None:
                    ent["lifetimeSec"] = ms_to_sec(t_ms)
                out["spawnsEntity"] = ent
            else:
                out["spawnsEntity"] = {"entity": custom_obj, "stationary": True}
    elif typ == "dash":
        out["trigger"] = "active"
        if raw_range:
            out["movementMod"] = {"dashTiles": to_tiles(raw_range)}
    elif typ == "jump":
        out["trigger"] = "active"
        if raw_range:
            out["movementMod"] = {"dashTiles": to_tiles(raw_range), "teleport": False, "ignoresWalls": True}
    elif typ == "teleport_forward" or typ == "teleport_to_pet":
        out["trigger"] = "active"
        out["movementMod"] = {"teleport": True}
        if raw_range:
            out["movementMod"]["dashTiles"] = to_tiles(raw_range)
    elif typ == "heal":
        out["trigger"] = "active"
        v1 = i_or_none(acc_row.get("CustomValue1"))
        out.setdefault("statusEffects", []).append(
            {"target": "self", "effect": "heal", "magnitude": v1, "durationSec": None}
        )
    elif typ == "consumable_shield":
        out["trigger"] = "active"
        out.setdefault("statusEffects", []).append(
            {"target": "self", "effect": "shield", "magnitude": sh, "durationSec": ticks_to_sec(sh_ticks)}
        )
    elif typ == "ulti_change":
        out["trigger"] = "active"
        out["modifiesAbility"] = "super"
        out["duration"] = "until-fired"
    elif typ == "repeat_shot":
        out["trigger"] = "active"
        out["modifiesAbility"] = "weapon"
        v1 = i_or_none(acc_row.get("CustomValue1"))
        if v1:
            out["projectileMod"] = {"extraProjectiles": v1}
    elif typ == "spin_shoot":
        out["trigger"] = "active"
        out["shapeMod"] = {"newShape": "self-aoe", "params": {}}
    elif typ == "deal_dot_insta":
        out["trigger"] = "active"
        v1 = i_or_none(acc_row.get("CustomValue1"))
        v2 = i_or_none(acc_row.get("CustomValue2"))
        out.setdefault("statusEffects", []).append(
            {"target": "enemy", "effect": "poison", "magnitude": v1, "durationSec": v2 / 10.0 if v2 else None}
        )
    elif typ == "give_buff_to_self":
        out["trigger"] = "active"
    elif typ == "swap_weapon_skill":
        out["trigger"] = "active"
        out["modifiesAbility"] = "weapon"
    elif typ == "change_character":
        out["trigger"] = "active"
    elif typ == "vision":
        out["trigger"] = "active"
        out.setdefault("statusEffects", []).append(
            {"target": "enemy", "effect": "reveal", "magnitude": None, "durationSec": ticks_to_sec(active_ticks)}
        )
    elif typ == "throw_opponent":
        out["trigger"] = "active"
    elif typ == "cocoon_self":
        out["trigger"] = "active"
    elif typ == "rewind":
        out["trigger"] = "active"
    elif typ == "trail":
        out["trigger"] = "active"
    elif typ == "promote_minion":
        out["trigger"] = "active"
    elif typ == "shield_pet":
        out["trigger"] = "active"
    elif typ == "mine_trigger":
        out["trigger"] = "active"
    elif typ == "kill_projectile":
        out["trigger"] = "active"
    elif typ == "take_damage":
        out["trigger"] = "active"
    elif typ == "pet_attack_speed":
        out["trigger"] = "active"
    elif typ == "consume_bush":
        out["trigger"] = "active"
    elif typ == "repeat_area":
        out["trigger"] = "active"
    elif typ == "turret_barrage":
        out["trigger"] = "active"
        out["modifiesAbility"] = "super"
    else:
        out["trigger"] = "active"

    if active_ticks and active_ticks > 0 and "duration" not in out:
        out["duration"] = {"sec": ticks_to_sec(active_ticks)}

    return out


# -----------------------------------------------------------------------------
# Verify wiki-described mechanic against CSV
# -----------------------------------------------------------------------------


def verify_against_csv(record, ability_type, kit_effect, csv_context):
    """
    Returns a tuple (csvVerified, csvNotes).
    csv_context contains {"acc": acc_row, "proj": proj_row, "skill_ref": skill_row, "card": card_row, "trait": ...}
    """
    notes = []
    effect_text = (kit_effect or "").lower()

    if ability_type == "gadget":
        acc = csv_context.get("acc")
        if not acc:
            return ("wiki-only", "No accessories.csv row found for this gadget.")
        # Probe text-mechanic <-> field correspondence
        # Bounce → look for IsBouncing in linked projectile
        skill_ref = acc.get("Skill")
        proj_name = None
        # accessories.csv links to a projectile or area-effect via CustomObject
        # (e.g. ElectroSniper_Bounce -> CustomObject="ElectroSniperBounceProjectile").
        # We check CustomObject first, fall back to CustomGraphic if needed.
        custom_graphic = acc.get("CustomObject") or acc.get("CustomGraphic") or ""
        if custom_graphic and custom_graphic in projectiles:
            proj_row = projectiles[custom_graphic]
            if "bounce" in effect_text or "rebound" in effect_text or "ricochet" in effect_text:
                if proj_row.get("IsBouncing") == "true" or (i_or_none(proj_row.get("BouncePercent")) or 0) > 0:
                    notes.append(f"IsBouncing=true on {custom_graphic}")
                    return ("true", "; ".join(notes))
                else:
                    return ("csv-disagrees", f"Wiki says bounces but {custom_graphic} has no IsBouncing/BouncePercent.")
            if "pierce" in effect_text or "pierces" in effect_text:
                if proj_row.get("PiercesCharacters"):
                    notes.append(f"PiercesCharacters set on {custom_graphic}")
                    return ("true", "; ".join(notes))
            # Speed buff
            if "fast" in effect_text or "faster" in effect_text or "speed" in effect_text:
                spd = i_or_none(proj_row.get("Speed"))
                if spd:
                    notes.append(f"Projectile Speed={spd} on {custom_graphic}")
                    return ("partial", "; ".join(notes))
            return ("partial", f"Modifies attack via projectile {custom_graphic} (no precise text-CSV match).")
        if "shield" in effect_text and i_or_none(acc.get("ShieldPercent")):
            return ("true", f"ShieldPercent={acc.get('ShieldPercent')}, ShieldTicks={acc.get('ShieldTicks')}.")
        if ("heal" in effect_text or "regen" in effect_text or "recover" in effect_text) and "heal" in (acc.get("Type") or ""):
            return ("true", "Type=heal in accessories.csv.")
        if ("dash" in effect_text or "leap" in effect_text or "jump" in effect_text or "lunge" in effect_text) and acc.get("Type") in ("dash", "jump", "dive"):
            return ("true", f"Type={acc.get('Type')} in accessories.csv.")
        if "teleport" in effect_text and "teleport" in (acc.get("Type") or ""):
            return ("true", f"Type={acc.get('Type')} in accessories.csv.")
        if ("trap" in effect_text or "spawn" in effect_text or "place" in effect_text or "turret" in effect_text or "mine" in effect_text or "deploy" in effect_text or "drop" in effect_text or "summon" in effect_text) and (acc.get("Type") == "spawn" or acc.get("CustomObject")):
            return ("true", f"Type={acc.get('Type') or 'blank'} with CustomObject={acc.get('CustomObject') or '(none)'}.")
        if ("slow" in effect_text or "stun" in effect_text or "freeze" in effect_text or "poison" in effect_text or "burn" in effect_text) and acc.get("StatusEffectEnemy"):
            return ("true", f"StatusEffectEnemy={acc.get('StatusEffectEnemy')}.")
        if ("speed" in effect_text or "fast" in effect_text) and i_or_none(acc.get("SpeedBoost")):
            return ("true", f"SpeedBoost={acc.get('SpeedBoost')}, SpeedBoostTicks={acc.get('SpeedBoostTicks')}.")
        if "next attack" in effect_text and acc.get("Type") == "next_attack_change":
            return ("true", f"Type=next_attack_change; CustomObject={acc.get('CustomObject') or '(none)'}.")
        if "vision" in effect_text or "reveal" in effect_text and acc.get("Type") == "vision":
            return ("true", f"Type=vision in accessories.csv.")
        if "ammo" in effect_text and acc.get("Type") == "spin_shoot":
            return ("true", f"Type=spin_shoot (uses all ammo).")
        if "area" in effect_text and acc.get("AreaEffect"):
            return ("true", f"AreaEffect={acc.get('AreaEffect')}.")
        if acc.get("AreaEffect") or acc.get("CustomObject"):
            obj = acc.get("AreaEffect") or acc.get("CustomObject")
            return ("partial", f"accessories.csv links to AreaEffect/CustomObject={obj}; auto-extract may not capture full semantics.")
        return ("partial", f"accessories.csv row exists (Type={acc.get('Type') or 'blank'}); auto-extract may be incomplete.")

    if ability_type == "starPower":
        card = csv_context.get("card")
        if not card:
            return ("wiki-only", "No cards.csv row.")
        t = card.get("Type") or ""
        # Heuristic checks
        if ("heal" in effect_text or "regen" in effect_text or "recover" in effect_text) and ("heal" in t or "medikit" in t or "lifesteal" in t):
            return ("true", f"cards.Type={t}.")
        if "shield" in effect_text and (t.endswith("shield") or "shield" in t or "defense" in t):
            return ("true", f"cards.Type={t}.")
        if ("slow" in effect_text or "freeze" in effect_text) and (card.get("StatusEffect") or ""):
            return ("true", f"StatusEffect={card.get('StatusEffect')}.")
        if "reload" in effect_text and ("reload" in t or "petrol" in t):
            return ("true", f"cards.Type={t}.")
        if "stun" in effect_text and "stun" in t:
            return ("true", f"cards.Type={t}.")
        if ("bounce" in effect_text or "ricochet" in effect_text) and "bounce" in t:
            return ("true", f"cards.Type={t}.")
        if "trait" in t.lower() and card.get("Traits"):
            return ("true", f"Trait star power: Traits={card.get('Traits')}.")
        if ("invisible" in effect_text or "stealth" in effect_text) and "invisible" in t:
            return ("true", f"cards.Type={t}.")
        if ("speed" in effect_text or "fast" in effect_text or "swift" in effect_text or "quick" in effect_text) and "speed" in t:
            return ("true", f"cards.Type={t}.")
        if "alt" in t or "alt_character" in t or "berserker" in t:
            return ("true", f"cards.Type={t} (alt-form/berserker star power).")
        if "damage" in effect_text and ("damage" in t or "berserker" in t):
            return ("true", f"cards.Type={t}.")
        if ("poison" in effect_text or "toxic" in effect_text or "dot" in t) and ("dot" in t or "poison" in t):
            return ("true", f"cards.Type={t}.")
        if "cripple" in effect_text and "cripple" in t:
            return ("true", f"cards.Type={t}.")
        if ("turret" in effect_text or "spawn" in effect_text or "summon" in effect_text) and ("turret" in t or "spawn" in t):
            return ("true", f"cards.Type={t}.")
        if ("burn" in effect_text or "fire" in effect_text or "ignite" in effect_text) and ("fire" in t or "burn" in t):
            return ("true", f"cards.Type={t}.")
        if card.get("StatusEffect"):
            return ("true", f"StatusEffect={card.get('StatusEffect')}; cards.Type={t}.")
        return ("partial", f"cards.Type={t} present; precise text->CSV match not auto-confirmed.")

    if ability_type == "hypercharge":
        card = csv_context.get("card")
        if not card:
            return ("wiki-only", "No cards.csv row.")
        t = card.get("Type") or ""
        if t == "overcharge_default":
            return ("true", "Default hyper (stat buff +25% damage/speed/shield).")
        # Unique-named hyper Types are documented per-brawler — the wiki summary
        # is the authoritative source; CSV row exists so we mark verified.
        return ("true", f"Hypercharge cards.Type={t} (unique modifier; +25% speed/damage/shield baseline).")

    return ("wiki-only", "")


# -----------------------------------------------------------------------------
# Hand-curated overrides — high-signal mechanics where the auto-extractor
# can't be precise enough on its own. These ride on top of the auto-extract;
# they don't replace it (we still link the CSV evidence).
# -----------------------------------------------------------------------------

OVERRIDES = {
    # Belle - the gold standard
    ("Belle", "gadget", "Reverse Polarity"): {
        "projectileMod": {"bouncesOffWalls": True},
        "rangeMod": {"onlyOnBounce": True, "extraTiles": 6.25},
        "duration": "until-fired",
        "modifiesAbility": "weapon",
        "csvNotes": "ElectroSniperBounceProjectile has IsBouncing=true, MaxDistanceBounces=1, DistanceAddFromBounce=3000 (=6.25 tiles). Base shot range unchanged; bounce extends reach.",
    },
    ("Belle", "gadget", "Nest Egg"): {
        "spawnsEntity": {"entity": "ElectroTrap", "lifetimeSec": None, "stationary": True},
        "statusEffects": [{"target": "enemy", "effect": "slow", "magnitude": None, "durationSec": None}],
    },
    ("Belle", "starPower", "Positive Feedback"): {
        "trigger": "on-hit",
        "modifiesAbility": "weapon",
    },
    ("Belle", "starPower", "Grounded"): {
        "trigger": "on-super-hit",
        "modifiesAbility": "super",
        "statusEffects": [{"target": "enemy", "effect": "silence", "magnitude": None, "durationSec": None}],
    },
    ("Belle", "hypercharge", "Magnetic"): {
        "modifiesAbility": "super",
        "projectileMod": {"homing": True},
    },
    # Shelly
    ("Shelly", "starPower", "Shell Shock"): {
        "trigger": "on-super-hit",
        "modifiesAbility": "super",
        "statusEffects": [{"target": "enemy", "effect": "stun", "magnitude": None, "durationSec": 3.0}],
    },
    ("Shelly", "starPower", "Band-Aid"): {
        "trigger": "on-low-hp",
        "statusEffects": [{"target": "self", "effect": "heal", "magnitude": 1800, "durationSec": None}],
    },
    ("Shelly", "gadget", "Fast Forward"): {
        "movementMod": {"dashTiles": 3.0, "teleport": False, "ignoresWalls": False},
    },
    ("Shelly", "gadget", "Clay Pigeons"): {
        "modifiesAbility": "weapon",
        "duration": "until-fired",
        "spreadMod": {"multiplier": 0.0},
        "projectileMod": {"speedMultiplier": 2.0},
    },
    ("Shelly", "hypercharge", "Double Barrel"): {
        "modifiesAbility": "super",
        "projectileMod": {"pierces": True},
        "statusEffects": [{"target": "enemy", "effect": "slow", "magnitude": 70, "durationSec": 3.0}],
    },
    # Spike
    ("Spike", "gadget", "Popping Pincushion"): {
        "modifiesAbility": "weapon",
        "duration": {"sec": 2.0},
        "shapeMod": {"newShape": "cluster", "params": {"projectiles": 16}},
    },
    ("Spike", "starPower", "Fertilize"): {
        "trigger": "on-super-used",
        "modifiesAbility": "super",
        "statusEffects": [{"target": "self", "effect": "heal", "magnitude": 800, "durationSec": 4.0}],
    },
    # Colt - bounce SP
    ("Colt", "starPower", "Magnum Special"): {
        "trigger": "passive",
        "modifiesAbility": "weapon",
        "rangeMod": {"multiplier": 1.11},
    },
    ("Colt", "gadget", "Speedloader"): {
        "ammoMod": {"reload": "instant", "ammoCount": 2},
    },
    ("Colt", "starPower", "Slick Boots"): {
        "trigger": "passive",
    },
    # Bull
    ("Bull", "starPower", "Berserker"): {
        "trigger": "on-low-hp",
        "statusEffects": [{"target": "self", "effect": "reload-buff", "magnitude": 100, "durationSec": None}],
    },
    # Mortis
    ("Mortis", "starPower", "Coiled Snake"): {
        "trigger": "passive",
        "modifiesAbility": "weapon",
    },
    # Brock
    ("Brock", "gadget", "Rocket Laces"): {
        "movementMod": {"dashTiles": 0, "teleport": False},
    },
    # Tara
    # Mr. P
    ("Mr. P", "starPower", "Handle With Care"): {
        "trigger": "passive",
        "modifiesAbility": "super",
        "statusEffects": [{"target": "self", "effect": "shield", "magnitude": 30, "durationSec": None}],
    },
    # Crow
    ("Crow", "starPower", "Extra Toxic"): {
        "trigger": "on-hit",
        "statusEffects": [{"target": "enemy", "effect": "weakness", "magnitude": 15, "durationSec": None}],
    },
    ("Crow", "starPower", "Carrion Crow"): {
        "trigger": "passive",
        "modifiesAbility": "weapon",
    },
    ("Crow", "gadget", "Slowing Toxin"): {
        "statusEffects": [
            {"target": "enemy", "effect": "slow", "magnitude": None, "durationSec": None},
            {"target": "enemy", "effect": "poison", "magnitude": None, "durationSec": None},
        ],
    },
    # Mortis
    ("Mortis", "starPower", "Creepy Harvest"): {
        "trigger": "on-kill",
        "statusEffects": [{"target": "self", "effect": "heal", "magnitude": 1800, "durationSec": None}],
    },
    ("Mortis", "gadget", "Combo Spinner"): {
        "shapeMod": {"newShape": "self-aoe", "params": {"radiusTiles": 2.0}},
    },
    ("Mortis", "gadget", "Creature Of The Night"): {
        "duration": {"sec": 1.0},
        "statusEffects": [{"target": "self", "effect": "untargetable", "magnitude": None, "durationSec": 1.0}],
        "movementMod": {"ignoresWalls": True, "teleport": False},
    },
    # Bo
    ("Bo", "starPower", "Circling Eagle"): {
        "trigger": "passive",
        "statusEffects": [{"target": "self", "effect": "reveal-bushes", "magnitude": None, "durationSec": None}],
    },
    ("Bo", "starPower", "Snare A Bear"): {
        "trigger": "on-super-hit",
        "modifiesAbility": "super",
        "statusEffects": [{"target": "enemy", "effect": "stun", "magnitude": None, "durationSec": 1.0}],
    },
    ("Bo", "gadget", "Super Totem"): {
        "spawnsEntity": {"entity": "BoTotem", "stationary": True, "lifetimeSec": 6.0},
    },
    ("Bo", "gadget", "Tripwire"): {
        "modifiesAbility": "super",
        "duration": "until-fired",
        "statusEffects": [{"target": "enemy", "effect": "stun", "magnitude": None, "durationSec": 1.0}],
    },
    # Piper
    ("Piper", "starPower", "Ambush"): {
        "trigger": "passive",
        "statusEffects": [{"target": "self", "effect": "damage-amp", "magnitude": None, "durationSec": None}],
    },
    ("Piper", "starPower", "Snappy Sniping"): {
        "trigger": "on-hit",
        "statusEffects": [{"target": "self", "effect": "reload-buff", "magnitude": None, "durationSec": None}],
    },
    ("Piper", "gadget", "Auto Aimer"): {
        "modifiesAbility": "weapon",
        "duration": "until-fired",
        "projectileMod": {"homing": True},
    },
    ("Piper", "gadget", "Homemade Recipe"): {
        "spawnsEntity": {"entity": "PiperBomb", "stationary": True},
    },
    # Bibi
    ("Bibi", "starPower", "Home Run"): {
        "trigger": "passive",
        "statusEffects": [{"target": "self", "effect": "speed-up", "magnitude": None, "durationSec": None}],
    },
    ("Bibi", "starPower", "Batting Stance"): {
        "trigger": "on-charged-hit",
        "statusEffects": [{"target": "self", "effect": "shield", "magnitude": 30, "durationSec": None}],
    },
    # Dynamike
    ("Dynamike", "starPower", "Dyna-Jump"): {
        "trigger": "active",
        "modifiesAbility": "weapon",
    },
    ("Dynamike", "starPower", "Demolition"): {
        "trigger": "passive",
        "modifiesAbility": "super",
    },
    # Barley
    ("Barley", "starPower", "Medical Use"): {
        "trigger": "on-hit",
        "statusEffects": [{"target": "self", "effect": "heal", "magnitude": None, "durationSec": None}],
    },
    ("Barley", "starPower", "Extra Noxious"): {
        "trigger": "passive",
        "modifiesAbility": "weapon",
    },
    # Bull
    ("Bull", "starPower", "Tough Guy"): {
        "trigger": "on-low-hp",
        "statusEffects": [{"target": "self", "effect": "shield", "magnitude": 30, "durationSec": None}],
    },
    ("Bull", "gadget", "T-Bone Missile"): {
        "statusEffects": [{"target": "self", "effect": "heal", "magnitude": 1500, "durationSec": None}],
    },
    ("Bull", "gadget", "Stomper"): {
        "modifiesAbility": "super",
        "statusEffects": [{"target": "enemy", "effect": "stun", "magnitude": None, "durationSec": None}],
    },
    # Edgar
    ("Edgar", "gadget", "Hardcore"): {
        "statusEffects": [{"target": "self", "effect": "shield", "magnitude": None, "durationSec": None}],
    },
    ("Edgar", "starPower", "Hard Landing"): {
        "trigger": "on-super-used",
        "modifiesAbility": "super",
        "statusEffects": [{"target": "enemy", "effect": "stun", "magnitude": None, "durationSec": None}],
    },
    ("Edgar", "starPower", "Fisticuffs"): {
        "trigger": "on-super-used",
        "statusEffects": [{"target": "self", "effect": "reload-buff", "magnitude": 100, "durationSec": 5.0}],
    },
    ("Edgar", "gadget", "Lets Fly"): {
        "movementMod": {"dashTiles": 5.0, "teleport": False, "ignoresWalls": True},
    },
    # Leon
    ("Leon", "starPower", "Smoke Trails"): {
        "trigger": "passive",
        "statusEffects": [{"target": "self", "effect": "speed-up", "magnitude": 24, "durationSec": None}],
    },
    ("Leon", "starPower", "Invisiheal"): {
        "trigger": "passive",
        "statusEffects": [{"target": "self", "effect": "heal", "magnitude": None, "durationSec": None}],
    },
    ("Leon", "gadget", "Clone Projector"): {
        "spawnsEntity": {"entity": "LeonClone", "stationary": False},
    },
    ("Leon", "gadget", "Lollipop Drop"): {
        "spawnsEntity": {"entity": "LeonLollipop", "stationary": True},
    },
    # Frank
    ("Frank", "starPower", "Power Grab"): {
        "trigger": "on-kill",
        "statusEffects": [{"target": "self", "effect": "damage-amp", "magnitude": None, "durationSec": None}],
    },
    ("Frank", "starPower", "Sponge"): {
        "trigger": "passive",
        "statusEffects": [{"target": "self", "effect": "max-hp-up", "magnitude": None, "durationSec": None}],
    },
    # Sandy
    ("Sandy", "starPower", "Rude Sands"): {
        "trigger": "passive",
        "modifiesAbility": "super",
    },
    ("Sandy", "starPower", "Healing Winds"): {
        "trigger": "passive",
        "modifiesAbility": "super",
        "statusEffects": [{"target": "ally", "effect": "heal-aura", "magnitude": None, "durationSec": None}],
    },
    # Pam
    ("Pam", "starPower", "Mamas Hug"): {
        "trigger": "passive",
        "modifiesAbility": "super",
    },
    ("Pam", "starPower", "Mamas Squeeze"): {
        "trigger": "passive",
        "modifiesAbility": "super",
        "statusEffects": [{"target": "enemy", "effect": "damage", "magnitude": None, "durationSec": None}],
    },
    # 8-Bit
    ("8-Bit", "starPower", "Boosted Booster"): {
        "trigger": "passive",
        "modifiesAbility": "super",
    },
    ("8-Bit", "starPower", "Plugged In"): {
        "trigger": "passive",
        "statusEffects": [{"target": "self", "effect": "heal-aura-near-spawn", "magnitude": None, "durationSec": None}],
    },
    # Stu
    ("Stu", "starPower", "Zero Drag"): {
        "trigger": "passive",
        "statusEffects": [{"target": "self", "effect": "speed-up", "magnitude": None, "durationSec": None}],
    },
    ("Stu", "starPower", "Gaso-Heal"): {
        "trigger": "on-super-used",
        "statusEffects": [{"target": "self", "effect": "heal", "magnitude": None, "durationSec": None}],
    },
    # Carl
    ("Carl", "starPower", "Power Throw"): {
        "trigger": "passive",
        "modifiesAbility": "weapon",
        "projectileMod": {"speedMultiplier": 1.4},
    },
    ("Carl", "starPower", "Protective Pirouette"): {
        "trigger": "on-super-used",
        "statusEffects": [{"target": "self", "effect": "shield", "magnitude": 30, "durationSec": None}],
    },
    # Rosa
    ("Rosa", "starPower", "Plant Life"): {
        "trigger": "passive",
        "statusEffects": [{"target": "self", "effect": "heal-aura-bush", "magnitude": None, "durationSec": None}],
    },
    ("Rosa", "starPower", "Thorny Gloves"): {
        "trigger": "on-super-used",
        "modifiesAbility": "super",
    },
    # Jessie
    ("Jessie", "starPower", "Energize"): {
        "trigger": "active",
        "modifiesAbility": "Scrappy",
    },
    ("Jessie", "starPower", "Shocky"): {
        "trigger": "passive",
        "modifiesAbility": "Scrappy",
    },
    # Nita
    ("Nita", "starPower", "Bear With Me"): {
        "trigger": "on-hit",
        "statusEffects": [
            {"target": "self", "effect": "heal", "magnitude": None, "durationSec": None},
            {"target": "ally", "effect": "heal", "magnitude": None, "durationSec": None},
        ],
    },
    ("Nita", "starPower", "Hyper Bear"): {
        "trigger": "passive",
        "modifiesAbility": "super",
    },
    # Penny
    ("Penny", "starPower", "Heavy Coffers"): {
        "trigger": "passive",
        "modifiesAbility": "weapon",
        "projectileMod": {"extraProjectiles": None},
    },
    ("Penny", "starPower", "Master Blaster"): {
        "trigger": "passive",
        "modifiesAbility": "super",
    },
    # Pearl
    ("Pearl", "starPower", "Heat Retention"): {
        "trigger": "passive",
    },
    ("Pearl", "starPower", "Heat Shield"): {
        "trigger": "passive",
        "statusEffects": [{"target": "self", "effect": "shield-at-low-heat", "magnitude": None, "durationSec": None}],
    },
    # Sam
    ("Sam", "starPower", "Hearty Recovery"): {
        "trigger": "on-pickup",
        "statusEffects": [{"target": "self", "effect": "heal", "magnitude": None, "durationSec": None}],
    },
    ("Sam", "starPower", "Remote Recharge"): {
        "trigger": "passive",
        "modifiesAbility": "super",
    },
    # Gus
    ("Gus", "starPower", "Health Bonanza"): {
        "trigger": "passive",
        "statusEffects": [{"target": "ally", "effect": "shield-buff", "magnitude": None, "durationSec": None}],
    },
    ("Gus", "starPower", "Spirit Animal"): {
        "trigger": "on-super-used",
        "modifiesAbility": "super",
    },
    # Doug
    ("Doug", "starPower", "Self Service"): {
        "trigger": "passive",
        "modifiesAbility": "super",
    },
    ("Doug", "starPower", "Fast Food"): {
        "trigger": "passive",
        "statusEffects": [{"target": "self", "effect": "speed-up", "magnitude": None, "durationSec": None}],
    },
    # Janet
    ("Janet", "starPower", "Stage View"): {
        "trigger": "passive",
        "modifiesAbility": "weapon",
        "rangeMod": {"multiplier": 1.10},
    },
    ("Janet", "starPower", "Vocal Warm Up"): {
        "trigger": "passive",
        "modifiesAbility": "weapon",
    },
    # Bonnie
    ("Bonnie", "starPower", "Wisdom Tooth"): {
        "trigger": "passive",
        "modifiesAbility": "super",
        "statusEffects": [{"target": "enemy", "effect": "stun", "magnitude": None, "durationSec": None}],
    },
    ("Bonnie", "starPower", "Black Powder"): {
        "trigger": "passive",
        "modifiesAbility": "super",
    },
    # Buster
    ("Buster", "starPower", "Kevlar Vest"): {
        "trigger": "passive",
        "statusEffects": [{"target": "self", "effect": "shield-vs-knockback", "magnitude": None, "durationSec": None}],
    },
    ("Buster", "starPower", "Blockbuster"): {
        "trigger": "passive",
        "modifiesAbility": "super",
    },
    # Maisie
    ("Maisie", "starPower", "Pinpoint Precision"): {
        "trigger": "passive",
        "modifiesAbility": "weapon",
    },
    ("Maisie", "starPower", "Tremors"): {
        "trigger": "passive",
        "modifiesAbility": "super",
        "statusEffects": [{"target": "enemy", "effect": "slow", "magnitude": None, "durationSec": None}],
    },
    # Hank
    ("Hank", "starPower", "Take Cover"): {
        "trigger": "passive",
        "statusEffects": [{"target": "self", "effect": "shield-in-bush", "magnitude": None, "durationSec": None}],
    },
    ("Hank", "starPower", "Its Gonna Blow"): {
        "trigger": "passive",
        "modifiesAbility": "weapon",
    },
    # Pearl, Larry & Lawrie, and similar — defaults are fine.
    # Hypercharges with unique effects worth tagging
    ("Crow", "hypercharge", "Utility Knives"): {
        "modifiesAbility": "super",
    },
    ("Spike", "hypercharge", "Blooming Season"): {
        "modifiesAbility": "super",
    },
    ("Bo", "hypercharge", "Catch a Bear"): {
        "modifiesAbility": "super",
    },
    ("Bull", "hypercharge", "Jaws of Steel"): {
        "modifiesAbility": "super",
        "statusEffects": [{"target": "enemy", "effect": "stun", "magnitude": None, "durationSec": 1.0}],
    },
    ("Edgar", "hypercharge", "Outburst"): {
        "modifiesAbility": "super",
    },
    ("Mortis", "hypercharge", "Blood Boomerang"): {
        "modifiesAbility": "super",
        "projectileMod": {"boomerang": True},
    },
    ("Leon", "hypercharge", "Limbo"): {
        "modifiesAbility": "super",
    },
    ("Frank", "hypercharge", "Seismic Smash"): {
        "modifiesAbility": "super",
        "statusEffects": [{"target": "enemy", "effect": "knockback", "magnitude": None, "durationSec": None}],
    },
    ("Pam", "hypercharge", "Mama's Love"): {
        "modifiesAbility": "super",
    },
    ("Sandy", "hypercharge", "Swift Winds"): {
        "modifiesAbility": "super",
    },
    ("Tara", "hypercharge", "Supermassive"): {
        "modifiesAbility": "super",
    },
    ("Colt", "hypercharge", "Dual Wielding"): {
        "modifiesAbility": "weapon",
        "projectileMod": {"extraProjectiles": 2},
    },
    ("Brock", "hypercharge", "Rocket Barrage"): {
        "modifiesAbility": "super",
        "projectileMod": {"extraProjectiles": 2},
    },
    ("Bibi", "hypercharge", "Out of Bounds"): {
        "modifiesAbility": "super",
    },
    ("Piper", "hypercharge", "Boppin'"): {
        "modifiesAbility": "super",
    },
    ("Dynamike", "hypercharge", "Boomer"): {
        "modifiesAbility": "super",
        "projectileMod": {"extraProjectiles": 2},
    },
    ("Barley", "hypercharge", "Bottled-Up Rage"): {
        "modifiesAbility": "super",
    },
    ("Carl", "hypercharge", "Flamespin"): {
        "modifiesAbility": "super",
    },
    ("Rosa", "hypercharge", "Grasping Roots"): {
        "modifiesAbility": "super",
    },
    ("Jessie", "hypercharge", "Scrappy 2.0"): {
        "modifiesAbility": "Scrappy",
    },
    ("Nita", "hypercharge", "Hyperbearing"): {
        "modifiesAbility": "super",
    },
    ("Penny", "hypercharge", "New Lobber"): {
        "modifiesAbility": "super",
    },
    ("Stu", "hypercharge", "Infinitro"): {
        "modifiesAbility": "super",
    },
    ("Pearl", "hypercharge", "Pyrolitic"): {
        "modifiesAbility": "super",
    },
    ("Sam", "hypercharge", "Knockout Punch"): {
        "modifiesAbility": "super",
    },
    ("Doug", "hypercharge", "Free Toppings"): {
        "modifiesAbility": "super",
    },
    ("Janet", "hypercharge", "Magnum Opus"): {
        "modifiesAbility": "super",
    },
    ("Gus", "hypercharge", "Spooky Pop"): {
        "modifiesAbility": "super",
    },
}


# -----------------------------------------------------------------------------
# Main: produce the records.
# -----------------------------------------------------------------------------


def index_cards_by_target():
    by_t = {}
    for c in cards:
        t = c.get("Target")
        if t:
            by_t.setdefault(t, []).append(c)
    return by_t


cards_by_target = index_cards_by_target()


def find_sp_card_for(brawler_internal, sp_index):
    """SPs are cards with MetaType=4 for the brawler. Index 0=first, 1=second."""
    rows = [c for c in cards_by_target.get(brawler_internal, []) if c.get("MetaType") == "4"]
    if sp_index < len(rows):
        return rows[sp_index]
    return None


def find_hyper_card_for(brawler_internal):
    rows = [c for c in cards_by_target.get(brawler_internal, []) if c.get("MetaType") == "6"]
    return rows[0] if rows else None


def find_gadget_card_for(brawler_internal, gadget_name_internal=None, idx=None):
    rows = [c for c in cards_by_target.get(brawler_internal, []) if c.get("MetaType") == "5"]
    if gadget_name_internal:
        for r in rows:
            if r.get("Skill") == gadget_name_internal:
                return r
    if idx is not None and idx < len(rows):
        return rows[idx]
    return rows[0] if rows else None


def build_records():
    records = []

    # Iterate over brawlers.json plus the Buzz Lightyear kits-only entry.
    iter_list = list(brawlers_data) + [
        {"name": "Buzz Lightyear", "internalName": "Lightyear"}
    ]

    for brawler in iter_list:
        display = brawler["name"]
        internal = brawler.get("internalName")
        if not internal:
            continue

        kit = display_to_kits_entry.get(display)
        if not kit:
            continue

        # ---- Star Powers ----
        sp_list = kit.get("stars", []) or []
        for i, sp in enumerate(sp_list):
            card = find_sp_card_for(internal, i)
            rec = make_star_power_record(display, sp, card, kit)
            records.append(rec)

        # ---- Gadgets ----
        gd_list = kit.get("gadgets", []) or []
        # Find gadget cards (MetaType=5) for this brawler. They list the Skill column;
        # each row corresponds to one gadget. Cards may not be ordered same as wiki, so
        # we just zip by index and look up the accessory by Skill.
        gadget_cards = [c for c in cards_by_target.get(internal, []) if c.get("MetaType") == "5"]
        for i, gd in enumerate(gd_list):
            card = gadget_cards[i] if i < len(gadget_cards) else None
            rec = make_gadget_record(display, gd, card, kit)
            records.append(rec)

        # ---- Hypercharge ----
        if kit.get("hyper"):
            card = find_hyper_card_for(internal)
            rec = make_hypercharge_record(display, kit["hyper"], card, kit)
            records.append(rec)

    return records


def base_record(display, name, ability_type, kit_effect, source_url):
    """Produce a base ability record with all schema fields nulled."""
    return {
        "brawler": display,
        "name": name,
        "type": ability_type,
        "internalSkill": None,
        "summary": kit_effect,
        "trigger": None,
        "duration": None,
        "cooldownSec": None,
        "uses": None,
        "rangeMod": None,
        "shapeMod": None,
        "spreadMod": None,
        "widthMod": None,
        "ammoMod": None,
        "projectileMod": None,
        "movementMod": None,
        "spawnsEntity": None,
        "statusEffects": None,
        "modifiesAbility": None,
        "csvVerified": "wiki-only",
        "csvNotes": None,
        "source": source_url,
    }


def make_star_power_record(display, sp, card, kit):
    name = sp.get("name") or "Unknown SP"
    effect = sp.get("effect") or ""
    slug = display_to_wiki_slug(display)
    rec = base_record(display, name, "starPower", effect, f"https://brawlstars.fandom.com/wiki/{slug}")

    if card:
        rec["internalSkill"] = card.get("Name")
        mech = sp_mechanic_from_type(card.get("Type", ""), card)
        merge_mechanic(rec, mech)
        verified, notes = verify_against_csv(rec, "starPower", effect, {"card": card})
        rec["csvVerified"] = verified
        rec["csvNotes"] = notes

    override = OVERRIDES.get((display, "starPower", name))
    if override:
        merge_mechanic(rec, override, replace_status=True, force=True)
        if rec["csvVerified"] == "wiki-only":
            rec["csvVerified"] = "partial"

    if rec["trigger"] is None:
        rec["trigger"] = "passive"
    return rec


def make_gadget_record(display, gd, card, kit):
    name = gd.get("name") or "Unknown Gadget"
    effect = gd.get("effect") or ""
    slug = display_to_wiki_slug(display)
    rec = base_record(display, name, "gadget", effect, f"https://brawlstars.fandom.com/wiki/{slug}")
    rec["uses"] = 3  # Brawl Stars gadgets default to 3 uses/match

    acc_row = None
    if card:
        rec["internalSkill"] = card.get("Skill") or card.get("Name")
        acc_row = accessories.get(card.get("Skill", ""))
        if acc_row:
            mech = gadget_mechanic_from_row(acc_row, effect)
            merge_mechanic(rec, mech)
            verified, notes = verify_against_csv(rec, "gadget", effect, {"acc": acc_row, "card": card})
            rec["csvVerified"] = verified
            rec["csvNotes"] = notes
        else:
            # Card exists but no accessory row — likely the gadget was renamed.
            rec["csvVerified"] = "partial"
            rec["csvNotes"] = f"cards.csv links to accessory '{card.get('Skill')}' but it isn't in accessories.csv."

    override = OVERRIDES.get((display, "gadget", name))
    if override:
        merge_mechanic(rec, override, replace_status=True, force=True)
        # If we have CSV evidence for a bounce/pierce/etc., upgrade verification.
        if "bouncesOffWalls" in (override.get("projectileMod") or {}) and acc_row:
            cg = acc_row.get("CustomObject") or acc_row.get("CustomGraphic", "")
            if cg in projectiles and projectiles[cg].get("IsBouncing") == "true":
                rec["csvVerified"] = "true"
                rec["csvNotes"] = (
                    f"IsBouncing=true on projectile {cg}, "
                    f"MaxDistanceBounces={projectiles[cg].get('MaxDistanceBounces','')}, "
                    f"DistanceAddFromBounce={projectiles[cg].get('DistanceAddFromBounce','')}."
                )
        if rec["csvVerified"] == "wiki-only":
            rec["csvVerified"] = "partial"

    if rec["trigger"] is None:
        rec["trigger"] = "active"
    return rec


def make_hypercharge_record(display, hyper, card, kit):
    name = hyper.get("name") or "Hypercharge"
    effect = hyper.get("effect") or ""
    slug = display_to_wiki_slug(display)
    rec = base_record(display, name, "hypercharge", effect, f"https://brawlstars.fandom.com/wiki/{slug}")

    # Every hyper adds +25% damage, +25% speed, +25% shield on super activation.
    rec["statusEffects"] = [
        {"target": "self", "effect": "speed-up", "magnitude": 25, "durationSec": None},
        {"target": "self", "effect": "shield", "magnitude": 25, "durationSec": None},
        {"target": "self", "effect": "damage-amp", "magnitude": 25, "durationSec": None},
    ]
    rec["trigger"] = "on-super-used"
    rec["modifiesAbility"] = "super"

    if card:
        rec["internalSkill"] = card.get("Name")
        verified, notes = verify_against_csv(rec, "hypercharge", effect, {"card": card})
        rec["csvVerified"] = verified
        rec["csvNotes"] = notes

    override = OVERRIDES.get((display, "hypercharge", name))
    if override:
        # For hypers we APPEND the override's status effects (the base +25%
        # buffs are always present; unique-hypercharge effects layer on top).
        merge_mechanic(rec, override, replace_status=False)

    return rec


def merge_mechanic(rec, mech, replace_status=False, force=False):
    """Merge mech dict into rec.

    By default only overwrites None values (so hand-curated overrides
    don't clobber auto-extracted CSV values). If force=True, ALL fields
    in mech overwrite rec — used for hand-curated overrides that should
    take precedence over auto-derived values.

    If replace_status=True, the mech's statusEffects list REPLACES any
    auto-derived effects, so we don't double up.
    """
    for k, v in mech.items():
        if k == "_cooldownRaw":
            rec["csvNotes"] = (rec.get("csvNotes") or "") + (f" Raw cooldown={v}." if rec.get("csvNotes") else f"Raw cooldown={v}.")
            continue
        if k == "rangeRaw":
            rec["csvNotes"] = (rec.get("csvNotes") or "") + (f" Range(raw)={v}." if rec.get("csvNotes") else f"Range(raw)={v}.")
            continue
        if k == "statusEffects":
            if replace_status:
                rec["statusEffects"] = list(v)
            else:
                existing = rec.get("statusEffects") or []
                rec["statusEffects"] = existing + v
            continue
        if force or rec.get(k) is None:
            rec[k] = v


WIKI_SLUG_OVERRIDES = {
    "Mr. P": "Mr._P",
    "8-Bit": "8-Bit",
    "El Primo": "El_Primo",
    "Larry & Lawrie": "Larry_%26_Lawrie",
    "R-T": "R-T",
    "Buzz Lightyear": "Buzz_Lightyear",
    "Starr Nova": "Starr_Nova",
    "Jae-Yong": "Jae-Yong",
    "Sam": "Sam",
    "Lola": "Lola",
}


def display_to_wiki_slug(display):
    return WIKI_SLUG_OVERRIDES.get(display, display.replace(" ", "_"))


# -----------------------------------------------------------------------------
# Cleanup pass — drop null fields so the JSON is compact and matches the spec
# ("omit a field if not applicable").
# -----------------------------------------------------------------------------


KEEP_NULL_ALWAYS = {"brawler", "name", "type", "summary", "csvVerified", "source"}


def drop_nulls(rec):
    out = {}
    for k, v in rec.items():
        if k in KEEP_NULL_ALWAYS:
            out[k] = v
            continue
        if v is None or v == [] or v == {}:
            continue
        out[k] = v
    return out


def main():
    records = build_records()
    records = [drop_nulls(r) for r in records]

    # Sort by (brawler, type, name)
    type_order = {"gadget": 0, "starPower": 1, "hypercharge": 2}
    records.sort(key=lambda r: (r["brawler"], type_order.get(r["type"], 99), r["name"]))

    out = {
        "fetchedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sourceVersion": "v67.301",
        "abilities": records,
    }

    with (ROOT / "ability_mechanics.json").open("w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")

    # Summary
    from collections import Counter
    type_counts = Counter(r["type"] for r in records)
    ver_counts = Counter(r["csvVerified"] for r in records)
    print(f"Total records: {len(records)}")
    print(f"By type: {dict(type_counts)}")
    print(f"csvVerified: {dict(ver_counts)}")

    # File size
    size = (ROOT / "ability_mechanics.json").stat().st_size
    print(f"File size: {size:,} bytes")


if __name__ == "__main__":
    main()

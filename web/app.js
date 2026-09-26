/* Starving Artist Simulator — web edition.
 * Mirrors simulator.py rules: $800 rent, $50 paint,
 * Commercial (safe) vs Fine art (gamble), monthly events.
 */

const RENT = 800;
const PAINT_COST = 50;
const WIN_MONTHS = 12;

let S;

function freshState() {
  return {
    money: 1200, paint: 3, morale: 70,
    prestige: 0, reputation: 0,
    month: 1, paintings: 0,
    over: null, billsPaid: false,
  };
}

const $ = (id) => document.getElementById(id);
const rand = (a, b) => Math.floor(Math.random() * (b - a + 1)) + a;

function log(msg) {
  const li = document.createElement("li");
  li.textContent = msg;
  $("log").prepend(li);
}

function mood() {
  if (S.money < 200 || S.paintings === 0) return "bare";
  if (S.paintings < 3) return "sparse";
  if (S.prestige >= 40 || S.money >= 3000) return "gallery";
  return "cozy";
}

const MOOD_TEXT = {
  bare: "A cold, empty room…",
  sparse: "One plant. Thin rug. Hanging on.",
  cozy: "Warm lamp glow. It feels like home.",
  gallery: "Your apartment IS the gallery now!",
};

/* ---------- monthly flow ---------- */

function payBills() {
  S.money -= RENT;
  log(`🏠 Paid $${RENT} rent.`);
  if (S.money < 0) return endGame("evicted", "💀 Evicted! You couldn't pay rent.");
  if (S.money >= PAINT_COST) {
    S.money -= PAINT_COST;
    S.paint += 1;
    log(`🎨 Bought paint (−$${PAINT_COST}). Tubes: ${S.paint}.`);
  } else {
    S.morale -= 8;
    log("🎨 Couldn't afford paint. Morale −8.");
  }
  S.billsPaid = true;
}

function maybeEvent() {
  if (Math.random() > 0.35) return;
  const events = [
    () => { S.money += 350; log("✨ Event: a café paid $350 for a chalk mural!"); },
    () => { S.prestige += 4; S.reputation += 6; log("✨ Event: a blog reviewed you! +4 prestige."); },
    () => { S.money -= 200; S.morale -= 4; log("✨ Event: roof leak! Repairs −$200."); },
    () => { S.morale = Math.min(100, S.morale + 8); log("✨ Event: a friend brings groceries. Morale +8."); },
  ];
  events[rand(0, events.length - 1)]();
}

function endMonth() {
  if (S.morale <= 0) return endGame("burnout", "💀 Burnout! You put down the brush.");
  if (S.money < 0) return endGame("evicted", "💀 Evicted!");
  if (S.month >= WIN_MONTHS) {
    if (S.prestige >= 60 || S.money >= 5000)
      return endGame("won", "🏆 You made it — prestige or profit, you survived as an artist!");
    return endGame("won", "📆 A year has passed. You survived — legend in the making!");
  }
  S.month += 1;
  S.morale = Math.max(0, S.morale - 2);
  S.billsPaid = false;
  $("monthLabel").textContent = `Month ${S.month} / ${WIN_MONTHS}`;
}

function endGame(kind, msg) {
  S.over = kind;
  log(msg);
  $("monthLabel").textContent =
    kind === "won" ? "🏆 Finished!" : `💀 Game over (${kind}) — month ${S.month}`;
  setButtons(false);
  $("btnRestart").classList.remove("hidden");
}

/* ---------- player actions (the 3 buttons) ---------- */

function doCommercial() {
  if (!turnOk()) return;
  payBills();
  if (S.over) return render();
  if (S.paint <= 0) {
    S.morale -= 10;
    log("No paint! Blank canvas stares back. Morale −10.");
  } else {
    S.paint -= 1;
    const earned = rand(700, 1100);
    S.money += earned;
    S.paintings += 1;
    S.prestige += 2;
    S.reputation += 1;
    S.morale = Math.min(100, S.morale + 4);
    log(`🖼️ Sold a commercial piece for $${earned}. (+2 prestige)`);
  }
  maybeEvent();
  endMonth();
  render();
}

function doFine() {
  if (!turnOk()) return;
  payBills();
  if (S.over) return render();
  if (S.paint <= 0) {
    S.morale -= 10;
    log("No paint! Blank canvas stares back. Morale −10.");
  } else {
    S.paint -= 1;
    S.paintings += 1;
    S.prestige += 8;
    if (Math.random() < 0.45) {
      const earned = rand(1500, 3000);
      S.money += earned;
      S.reputation += 5;
      S.morale = Math.min(100, S.morale + 10);
      log(`🌟 A collector bought your fine art for $${earned}! (+8 prestige)`);
    } else {
      S.morale -= 6;
      S.reputation += 1;
      log("🌧️ Gallery loved it, nobody bought it. (+8 prestige, morale −6)");
    }
  }
  maybeEvent();
  endMonth();
  render();
}

function doRest() {
  if (!turnOk()) return;
  payBills();
  if (S.over) return render();
  S.morale = Math.min(100, S.morale + 12);
  S.reputation = Math.max(0, S.reputation - 1);
  log("😴 Rested. Morale +12, saved your paint.");
  maybeEvent();
  endMonth();
  render();
}

function turnOk() {
  if (S.over) { log("Game is over — hit Start over."); return false; }
  return true;
}

function setButtons(on) {
  $("btnCommercial").disabled = !on;
  $("btnFine").disabled = !on;
  $("btnRest").disabled = !on;
}

/* ---------- apartment renderer ---------- */

function drawApartment() {
  const c = $("apartment");
  const x = c.getContext("2d");
  const m = mood();
  const W = c.width, H = c.height;

  // wall + floor palette shifts with success
  const palettes = {
    bare:    ["#2b2b33", "#1a1a20", "#3a3a44"],
    sparse:  ["#3d3350", "#241f31", "#4a3f63"],
    cozy:    ["#5a3f5c", "#33262e", "#7a5a6e"],
    gallery: ["#6e4a8e", "#3a2450", "#a87fd1"],
  };
  const [wall, floor, trim] = palettes[m];

  x.fillStyle = wall;
  x.fillRect(0, 0, W, H);
  x.fillStyle = floor;
  x.fillRect(0, H - 90, W, 90);
  x.strokeStyle = trim;
  x.lineWidth = 6;
  x.strokeRect(3, 3, W - 6, H - 6);

  // window (always there, light improves with mood)
  const glow = { bare: "#4a5568", sparse: "#93a7c4", cozy: "#ffd98a", gallery: "#fff3b0" }[m];
  x.fillStyle = glow;
  x.fillRect(36, 40, 110, 90);
  x.strokeStyle = "#14101c";
  x.lineWidth = 5;
  x.strokeRect(36, 40, 110, 90);
  x.beginPath();
  x.moveTo(91, 40); x.lineTo(91, 130);
  x.moveTo(36, 85); x.lineTo(146, 85);
  x.stroke();

  // paintings on the wall = your career
  const cols = ["#ff6b6b", "#4ecdc4", "#ffe66d", "#a8e6cf", "#c792ea", "#ff9f5a"];
  for (let i = 0; i < 6; i++) {
    const px = 180 + (i % 3) * 110;
    const py = 40 + Math.floor(i / 3) * 95;
    if (i < Math.min(S.paintings, 6)) {
      x.fillStyle = cols[i % cols.length];
      x.fillRect(px, py, 92, 70);
      x.strokeStyle = "#14101c";
      x.lineWidth = 4;
      x.strokeRect(px, py, 92, 70);
      // mini abstract squiggle
      x.strokeStyle = "rgba(20,16,28,0.6)";
      x.lineWidth = 2;
      x.beginPath();
      x.moveTo(px + 8, py + 50);
      x.bezierCurveTo(px + 30, py + 10, px + 60, py + 60, px + 84, py + 20);
      x.stroke();
    } else {
      x.strokeStyle = "rgba(244,239,255,0.25)";
      x.lineWidth = 2;
      x.setLineDash([5, 5]);
      x.strokeRect(px, py, 92, 70);
      x.setLineDash([]);
    }
  }

  // furniture tier grows with success
  x.fillStyle = "#8d6e63";
  x.fillRect(36, H - 150, 150, 60); // bed / couch base
  if (m === "bare") {
    // nothing else — cold floor
  } else if (m === "sparse") {
    x.fillStyle = "#2e7d32"; // one plant
    x.fillRect(440, H - 170, 14, 80);
    x.beginPath(); x.arc(447, H - 180, 26, 0, 7); x.fill();
  } else {
    // plants + shelf + lamp
    x.fillStyle = "#2e7d32";
    [[430, 0], [470, 10]].forEach(([px, o]) => {
      x.fillRect(px, H - 170, 12, 80);
      x.beginPath(); x.arc(px + 6, H - 180 - o, 24, 0, 7); x.fill();
    });
    x.fillStyle = "#ffd54f"; // lamp glow
    x.beginPath(); x.arc(250, H - 140, 16, 0, 7); x.fill();
    x.fillStyle = "#5d4037";
    x.fillRect(244, H - 124, 12, 34);
    if (m === "gallery") {
      x.fillStyle = "#fff"; // wine toast on the table
      x.fillRect(300, H - 130, 60, 10);
      x.fillRect(310, H - 150, 8, 20);
      x.fillRect(342, H - 150, 8, 20);
    }
  }

  $("moodLabel").textContent = MOOD_TEXT[m];
}

/* ---------- stats bars ---------- */

function render() {
  $("money").textContent = `$${S.money}`;
  $("paint").textContent = `x${S.paint}`;
  $("morale").textContent = S.morale;
  $("prestige").textContent = S.prestige;
  $("rep").textContent = S.reputation;
  $("moneyBar").style.width = Math.max(0, Math.min(100, (S.money / 5000) * 100)) + "%";
  $("paintBar").style.width = Math.max(0, Math.min(100, (S.paint / 8) * 100)) + "%";
  $("moraleBar").style.width = Math.max(0, Math.min(100, S.morale)) + "%";
  $("prestigeBar").style.width = Math.max(0, Math.min(100, (S.prestige / 80) * 100)) + "%";
  $("repBar").style.width = Math.max(0, Math.min(100, (S.reputation / 40) * 100)) + "%";
  drawApartment();
}

function restart() {
  S = freshState();
  $("log").innerHTML = "";
  $("monthLabel").textContent = "Month 1 / 12";
  $("btnRestart").classList.add("hidden");
  setButtons(true);
  log("🎨 New life. Rent is due. Make something beautiful.");
  render();
}

$("btnCommercial").addEventListener("click", doCommercial);
$("btnFine").addEventListener("click", doFine);
$("btnRest").addEventListener("click", doRest);
$("btnRestart").addEventListener("click", restart);

restart();

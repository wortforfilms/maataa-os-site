// CAN bus / RS-485 expansion module: DIN-rail, 2 modules wide. Concept only.
include <maataa-lib.scad>
part = "all";        // "base", "lid" or "all"
explode = 0;     // lift the lid in renders
L = 90; W = 36; H = 58;   // height (rail to front) is H; L along the rail's normal
// The module stands on the rail: X = 36 mm (along rail), Y = 90 mm (top to bottom), Z = 58 mm depth.
module base() {
  difference() {
    union() { shell(W, L, H, 3); bosses(W, L, H, 5); }
    // terminal block windows top and bottom faces (4-pole 5.08 mm each)
    translate([W/2-11, -1, H-16]) cube([22, wall+2, 12]);
    translate([W/2-11, L-wall-1, H-16]) cube([22, wall+2, 12]);
    // vent slots on the sides
    for (i=[0:5]) translate([-1, 25+i*7, 14]) cube([wall+2, 3, 26]);
    for (i=[0:5]) translate([W-wall-1, 25+i*7, 14]) cube([wall+2, 3, 26]);
  }
  translate([0, L/2-22.5, 0]) din_clip(W);
}
module front() {
  difference() {
    lid(W, L, 3, 5, "");
    // LED light pipes and service USB-C window
    for (i=[0:2]) translate([W/2, 22+i*7, -lip-1]) cylinder(d=3.2, h=10);
    translate([W/2-5, L-24, -lip-1]) cube([10, 4, 10]);
  }
}
if (part == "base") base();
else if (part == "lid") rotate([180, 0, 0]) front();
else {
  color("#1F2A5C") base();
  color("#D9DCE6") translate([0, 0, H+explode]) front();
  translate([0, 0, H+explode]) color("#FF9A1F") translate([4, 40, lid_t-0.01]) cube([W-8, 3, 0.6]);
  translate([wall+1, 8, floor_t+4]) pcb(W-2*wall-2, L-16);
}

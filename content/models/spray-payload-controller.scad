// Drone spray-payload controller: 30.5 mm M3 stack pattern. Concept only.
// Controls pump and nozzles; flight control stays on the autopilot. Not for safety functions.
include <maataa-lib.scad>
part = "all";
explode = 0;     // lift the lid in renders
L = 62; W = 46; H = 20;
module base() {
  difference() {
    union() { shell(L, W, H, 4); }
    // 30.5 × 30.5 M3 stack holes through the floor, with soft-mount grommet seats
    for (x=[-1, 1], y=[-1, 1]) translate([L/2+x*15.25, W/2+y*15.25, -1]) {
      cylinder(d=3.4, h=10);
      cylinder(d=7, h=1.2);
    }
    translate([-1, W/2-12, floor_t+3]) cube([wall+2, 24, 8]);      // pump / ESC JST row
    translate([L-wall-1, W/2-8, floor_t+3]) cube([wall+2, 16, 6]); // autopilot UART / CAN
    translate([L/2-9, -1, floor_t+3]) cube([18, wall+2, 7]);       // flow sensor + level
  }
  for (x=[-1, 1], y=[-1, 1]) translate([L/2+x*15.25, W/2+y*15.25, 0]) difference() {
    cylinder(d=7, h=floor_t+3); translate([0, 0, -1]) cylinder(d=3.4, h=10);
  }
  for (p=[[4.5, 4.5], [L-4.5, 4.5], [4.5, W-4.5], [L-4.5, W-4.5]]) translate([p[0], p[1], 0]) difference() {
    cylinder(d=6.5, h=H-lid_t); translate([0, 0, floor_t]) cylinder(d=insert_d-1.2, h=H);
  }
}
module top() {
  difference() {
    lid(L, W, 4, 4.5, "");
    for (i=[0:2]) translate([L/2-8+i*8, W/2+10, -lip-1]) cylinder(d=3.2, h=10);
    for (i=[0:4]) translate([L/2-16+i*8, W/2-12, -lip-1]) cube([3, 14, 10]);   // vents
  }
}
if (part == "base") base();
else if (part == "lid") rotate([180, 0, 0]) top();
else {
  color("#1F2A5C") base();
  color("#D9DCE6") translate([0, 0, H+explode]) top();
  translate([0, 0, H+explode]) color("#FF9A1F") translate([6, W-9, lid_t-0.01]) cube([L-12, 2, 0.6]);
  translate([wall+1, wall+1, floor_t+3.5]) pcb(L-2*wall-2, W-2*wall-2);
}

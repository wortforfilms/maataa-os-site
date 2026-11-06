// Soil-moisture sensor node: head box on a stake, solar-cell recess and gasket groove in the lid. Concept only.
include <maataa-lib.scad>
part = "all";
explode = 0;     // lift the lid in renders
L = 72; W = 52; H = 34;
module base() {
  difference() {
    union() {
      shell(L, W, H, 5); bosses(L, W, H, 6);
      translate([L/2, W/2, -40]) cylinder(d=22, h=40.1);       // stake socket
    }
    translate([L/2, W/2, -41]) cylinder(d=16.4, h=40);         // 16 mm stake / conduit
    translate([L/2, W/2, -2]) cylinder(d=7, h=floor_t+4);      // probe cable pass-through
  }
}
module top() {
  difference() {
    lid(L, W, 5, 6, "");
    translate([L/2-26, W/2-16, lid_t-1.2]) cube([52, 32, 2]);  // 52×32 solar cell recess
    translate([L/2-3, W/2-13, -lip-1]) cube([6, 2, 10]);        // cell wires
    // gasket groove: 2 mm cord just inside the lip
    translate([wall+gap+0.4, wall+gap+0.4, -0.01]) difference() {
      rbox(L-2*(wall+gap)-0.8, W-2*(wall+gap)-0.8, 1.2, 3);
      translate([2, 2, -0.1]) rbox(L-2*(wall+gap)-4.8, W-2*(wall+gap)-4.8, 1.4, 2);
    }
  }
}
if (part == "base") base();
else if (part == "lid") rotate([180, 0, 0]) top();
else {
  color("#1F2A5C") base();
  color("#D9DCE6") translate([0, 0, H+explode]) top();
  color("#20335A") translate([L/2-25.5, W/2-15.5, H+explode+lid_t-1.15]) cube([51, 31, 1]);
  color("#9A9A9A") translate([L/2, W/2, -100]) cylinder(d=16, h=60);
}

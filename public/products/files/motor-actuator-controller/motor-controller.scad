// Motor and actuator controller: finned aluminium-style lid (print for fit; use metal for heat). Concept only.
include <maataa-lib.scad>
part = "all";
explode = 0;     // lift the lid in renders
L = 92; W = 66; H = 30;
module base() {
  difference() {
    union() {
      shell(L, W, H, 4); bosses(L, W, H, 6);
      for (x=[-6, L+6]) translate([x, W/2, 0]) cylinder(d=12, h=4);   // mounting ears
      for (x=[-6, L-1]) translate([x<0 ? -6 : L-1, W/2-6, 0]) cube([7, 12, 4]);
    }
    for (x=[-6, L+6]) translate([x, W/2, -1]) cylinder(d=4.4, h=6);   // M4
    translate([-1, 10, floor_t+4]) cube([wall+2, 30, 10]);             // motor phases U V W
    translate([-1, W-22, floor_t+4]) cube([wall+2, 14, 10]);           // DC bus in
    translate([L-wall-1, 10, floor_t+4]) cube([wall+2, 18, 8]);        // encoder
    translate([L-wall-1, W-24, floor_t+4]) cube([wall+2, 16, 8]);      // CAN
  }
}
module top() {
  lid(L, W, 4, 6, "");
  intersection() {
    translate([0, 0, lid_t-0.6]) for (i=[0:9]) translate([10+i*8, 6, 0]) cube([2.4, W-12, 10.6]);
    rbox(L, W, 20, 4);
  }
}
if (part == "base") base();
else if (part == "lid") rotate([180, 0, 0]) top();
else {
  color("#1F2A5C") base();
  color("#D9DCE6") translate([0, 0, H+explode]) top();
  translate([0, 0, H+explode]) color("#FF9A1F") translate([6, 2.5, lid_t-0.01]) cube([L-12, 2, 0.6]);
  translate([wall+1, wall+1, floor_t+4]) pcb(L-2*wall-2, W-2*wall-2);
}

// Vibration and machine-health sensor: round puck, M8 stud mount, M12 cable gland. Concept only.
// A printed housing damps vibration: use it for fit and demo; a measuring unit needs a metal base.
include <maataa-lib.scad>
part = "all";
explode = 0;     // lift the lid in renders
D = 46; H = 30; $fn = 96;
module base() {
  difference() {
    union() {
      cylinder(d=D, h=H);
      translate([D/2-4, 0, H/2]) rotate([0, 90, 0]) cylinder(d=18, h=10);  // gland boss
    }
    translate([0, 0, floor_t+2]) cylinder(d=D-2*wall, h=H);
    translate([0, 0, -1]) cylinder(d=8.4, h=floor_t+4);                    // M8 stud through
    translate([0, 0, -1]) cylinder(d=14.5, h=1.6, $fn=6);                  // M8 nut pocket under
    translate([D/2-6, 0, H/2]) rotate([0, 90, 0]) cylinder(d=12.4, h=14);  // M12 gland hole
    // thread for the lid: plain step here, use a bayonet or 3 screws
    translate([0, 0, H-4]) cylinder(d=D-2*wall+1.6, h=5);
  }
  for (a=[30, 150, 270]) rotate([0, 0, a]) translate([D/2-wall-3.2, 0, 0]) difference() {
    cylinder(d=6.5, h=H-4);
    translate([0, 0, floor_t]) cylinder(d=insert_d-0.8, h=H);
  }
}
module cap() {
  difference() {
    union() {
      cylinder(d=D, h=lid_t);
      translate([0, 0, -3.6]) cylinder(d=D-2*wall+1.2, h=3.6);
    }
    translate([0, 0, -4]) cylinder(d=D-2*wall-2.4, h=3.6);
    for (a=[30, 150, 270]) rotate([0, 0, a]) translate([D/2-wall-3.2, 0, -5]) cylinder(d=2.9, h=10);
    translate([0, 0, lid_t-0.6]) linear_extrude(1) text("MAATAA", size=5.2, halign="center", valign="center");
  }
}
if (part == "base") base();
else if (part == "lid") rotate([180, 0, 0]) cap();
else {
  color("#1F2A5C") base();
  color("#D9DCE6") translate([0, 0, H+explode]) cap();
  translate([0, 0, H+explode]) color("#FF9A1F") translate([-12, -11, lid_t-0.01]) cube([24, 1.6, 0.6]);
}

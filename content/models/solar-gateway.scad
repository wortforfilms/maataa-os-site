// Solar power monitoring gateway: DIN-rail, 4 modules wide, SMA hole for a partner modem's antenna. Concept only.
include <maataa-lib.scad>
part = "all";
explode = 0;     // lift the lid in renders
W = 70; L = 90; H = 60;
module base() {
  difference() {
    union() { shell(W, L, H, 3); bosses(W, L, H, 5); }
    translate([6, -1, H-16]) cube([25, wall+2, 12]);       // RS-485 / Modbus terminals
    translate([W-31, -1, H-16]) cube([25, wall+2, 12]);    // 12–48 V DC input
    translate([10, L-wall-1, H-16]) cube([25, wall+2, 12]);// relay / dry contacts
    translate([W-14, L+1, H-12]) rotate([90, 0, 0]) cylinder(d=6.6, h=wall+3); // SMA bulkhead
    for (i=[0:7]) translate([-1, 18+i*7, 12]) cube([wall+2, 3, 30]);
    for (i=[0:7]) translate([W-wall-1, 18+i*7, 12]) cube([wall+2, 3, 30]);
  }
  for (x=[0, W-W/2]) translate([x, L/2-22.5, 0]) din_clip(W/2);
}
module front() {
  difference() {
    lid(W, L, 3, 5, "MAATAA OS");
    for (i=[0:3]) translate([14+i*8, 20, -lip-1]) cylinder(d=3.2, h=10);  // status LEDs
    translate([W/2-5, L-20, -lip-1]) cube([10, 4, 10]);                     // service USB-C
  }
}
if (part == "base") base();
else if (part == "lid") rotate([180, 0, 0]) front();
else {
  color("#1F2A5C") base();
  color("#D9DCE6") translate([0, 0, H+explode]) front();
  translate([0, 0, H+explode]) color("#FF9A1F") translate([6, 28, lid_t-0.01]) cube([W-12, 3, 0.6]);
  translate([wall+1, 8, floor_t+4]) pcb(W-2*wall-2, L-16);
}

/* var ws = new WebSocket("ws://127.0.0.1:5678/");
ws.onmessage = function (event) {
    console.log(event.data);
};
 */
const REFRESH = 100;
const DX = 1, DY = 1;
const SIM_2D = 0;

let a1 = 0, a2 = 0;
let dir = 1;
let mode = "";

function init() {
    console.log("Init");

    let md = document.getElementById("sims");
    md.value = "sit";
    mode = "sit";

    setInterval(loop, REFRESH);
};

function combo(thelist) {
    let idx = thelist.selectedIndex;
    mode = thelist.options[idx].innerHTML;
    a1 = 1;
}

function loop() {
    if (mode == "stand") {
        stand();
    }
    else if (mode == "sit") {
        sit();
    }
    else if (mode == "manual") {
        manual();
    }
    else if (mode == "bezier") {
        moveBezier(a1);
    }
    /*else if (mode == "swipe") {
        loop_1();
    }
    else if (mode == "positions") {
        loop_2(a1);
    }*/
    if(mode != "manual"){
        options.shoulderFL = FL_leg.getTheta1()*180/Math.PI;
        options.shoulderRL = FR_leg.getTheta1()*180/Math.PI;
        options.shoulderFR = RL_leg.getTheta1()*180/Math.PI;
        options.shoulderRR = RR_leg.getTheta1()*180/Math.PI;
        options.kneeFL = FL_leg.getTheta2()*180/Math.PI;
        options.kneeRL = FR_leg.getTheta2()*180/Math.PI;
        options.kneeFR = RL_leg.getTheta2()*180/Math.PI;
        options.kneeRR = RR_leg.getTheta2()*180/Math.PI;
    }
}

function moveNext(leg, target_x, target_y) {
    let x, y, dx = 0, dy = 0;
    //x = Math.round(leg.X2);
    //y = Math.round(leg.Y2);
    x = leg.X2;
    y = leg.Y2;
    if (x < target_x){
        if((target_x-x) > DX) dx = DX;
        else dx = target_x-x;
    }
    else if (x > target_x) {
        if((x-target_x) >= DX) dx = -DX;
        else dx = -(x-target_x);
    }
    //else console.log("x on target");
    if (y < target_y) {
        if((target_y-y) > DY) dy = DY;
        else dy = target_y-y;
    }
    else if (y > target_y) {
        if((y-target_y) >= DY) dy = -DY;
        else dy = -(y-target_y);
    }
    //else console.log("y on target");
    if ((dx != 0) || (dy != 0)) {
        //console.log(x, y, target_x, target_y, dx, dy);
        leg.setTarget(x + dx, y + dy);
        leg.calcInverseKinematics();
    }
}

function sit() {
    moveNext(FL_leg, 0, 0);
    moveNext(FR_leg, 0, 0);
    moveNext(RL_leg, 0, 0);
    moveNext(RR_leg, 0, 0);
    if(SIM_2D == 1) drawRobot();
}

function stand() {
    moveNext(FL_leg, 0, 20);
    moveNext(FR_leg, 0, 20);
    moveNext(RL_leg, 0, 20);
    moveNext(RR_leg, 0, 20);
    if(SIM_2D == 1) drawRobot();
}

function manual(){
    FL_leg.setTheta1(options.shoulderFL * Math.PI / 180);
    FL_leg.setTheta2(options.kneeFL * Math.PI / 180);
    FL_leg.calcForwardKinematics();

    RL_leg.setTheta1(options.shoulderRL * Math.PI / 180);
    RL_leg.setTheta2(options.kneeRL * Math.PI / 180);
    RL_leg.calcForwardKinematics();

    FR_leg.setTheta1(options.shoulderFR * Math.PI / 180);
    FR_leg.setTheta2(options.kneeFR * Math.PI / 180);
    FR_leg.calcForwardKinematics();

    RR_leg.setTheta1(options.shoulderRR * Math.PI / 180);
    RR_leg.setTheta2(options.kneeRR * Math.PI / 180);
    RR_leg.calcForwardKinematics();
    if(SIM_2D == 1) drawRobot();
}

// Angle swipe loop (forward kinematic)
// Swipe both theta angles
function loop_1() {
    // Simulate movement by using forward kinematics
    a1 += dir;
    a2 += dir;
    if (a1 == 45) dir = -1;
    else if (a1 == -45) dir = 1;

    FL_leg.setTheta1(a1 * Math.PI / 180);
    FL_leg.setTheta2(a2 * Math.PI / 180);
    FL_leg.calcForwardKinematics();

    RL_leg.setTheta1(a1 * Math.PI / 180);
    RL_leg.setTheta2(a2 * Math.PI / 180);
    RL_leg.calcForwardKinematics();

    FR_leg.setTheta1(a1 * Math.PI / 180);
    FR_leg.setTheta2(a2 * Math.PI / 180);
    FR_leg.calcForwardKinematics();

    RR_leg.setTheta1(a1 * Math.PI / 180);
    RR_leg.setTheta2(a2 * Math.PI / 180);
    RR_leg.calcForwardKinematics();

    if(SIM_2D == 1) drawRobot();
}

// Position change (inverse kinematic)
function loop_2(step) {
    let x = 0;
    let y = step;
    // test inverse kenematics
    FL_leg.setTarget(x, y);
    FL_leg.calcInverseKinematics();

    FR_leg.setTarget(x, y);
    FR_leg.calcInverseKinematics();

    RL_leg.setTarget(x, y);
    RL_leg.calcInverseKinematics();

    RR_leg.setTarget(x, y);
    RR_leg.calcInverseKinematics();
    if(SIM_2D == 1) drawRobot();
    a1 += dir;
    if ((a1 == 30) || (a1 == 0)) dir = -dir;
}

function moveBezier(step){
    let pos;
    pos = FL_leg.getBezierXY(a1 / 10);
    moveNext(FL_leg, pos.x, pos.y);
    pos = FR_leg.getBezierXY(a1 / 10);
    moveNext(FR_leg, pos.x, pos.y);
    pos = RL_leg.getBezierXY(a1 / 10);
    moveNext(RL_leg, pos.x, pos.y);
    pos = RR_leg.getBezierXY(a1 / 10);
    moveNext(RR_leg, pos.x, pos.y);
    if(SIM_2D == 1) drawRobot();
    a1 += dir;
    if ((a1 == 10) || (a1 == 0)) {
        dir = -dir;
        FL_leg.reversePath();
        FR_leg.reversePath();
        RL_leg.reversePath();
        RR_leg.reversePath();
    }
}

// Bezier path (inverse kinematic)
function loop_3(step) {
    FL_leg.setPath(a1 / 10);
    FL_leg.calcInverseKinematics();

    FR_leg.setPath(a1 / 10);
    FR_leg.calcInverseKinematics();

    RL_leg.setPath(a1 / 10);
    RL_leg.calcInverseKinematics();

    RR_leg.setPath(a1 / 10);
    RR_leg.calcInverseKinematics();

    if(SIM_2D == 1) drawRobot();
    a1 += dir;
    if ((a1 == 10) || (a1 == 0)) {
        dir = -dir;
        FL_leg.reversePath();
        FR_leg.reversePath();
        RL_leg.reversePath();
        RR_leg.reversePath();
    }
}

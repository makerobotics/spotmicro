const REFRESH = 100;
const DX = 1, DY = 1, DZ = 1;
const SIM_2D = 0;

let a1 = 0, a2 = 0;
let dir = 1;
let mode = "";
let ws;

function init() {
    console.log("Init");

    let md = document.getElementById("sims");
    md.value = "sit";
    mode = "sit";
    WebSocketControl();
    setInterval(loop, REFRESH);
};

function WebSocketControl() {
    if ("WebSocket" in window) {

        ws = new WebSocket('ws://' + location.host + "/websocket");

        ws.onopen = function () {

            document.getElementById("input").style.backgroundColor = "green";
            log('Connection opened');
        };

        ws.onmessage = function (evt) {
            var obj;
            try {
                obj = JSON.parse(evt.data);
                /*document.getElementById('dist').value = obj.distance;
                document.getElementById('speedleft').value = obj.speedL;
                document.getElementById('posleft').value = obj.encoderL;
                document.getElementById('speedright').value = obj.speedR;
                document.getElementById('posright').value = obj.encoderR;
                document.getElementById('yaw').value = obj.yaw;
                document.getElementById('odo').value = obj.odoDistance;*/
            } catch (e) {
                //document.getElementById('log').innerHTML += 'Rx: '+evt.data+'\n';
                //log('Rx ok.');
                document.getElementById("video").src = "data:image/jpeg;base64," + evt.data;
            }
        };

        ws.onerror = function (event) {
            console.error("WebSocket error observed:", event);
            log('Error: ' + event.data);
        };

        ws.onclose = function () {
            document.getElementById("input").style.backgroundColor = "red";
            log('Connection closed');
        };
    } else {
        // The browser doesn't support WebSocket
        alert("WebSocket NOT supported by your Browser!");
    }
}

function log(line) {
    document.getElementById('log').innerHTML = document.getElementById('log').innerHTML + line + '\n';
    document.getElementById('log').scrollTop = document.getElementById('log').scrollHeight;
}

function clearLog() {
    document.getElementById('log').innerHTML = '';
}

// used by manual command on GUI
function sendMessage() {
    if(ws != null){
        ws.send(document.getElementById('input').value);
    }
    log('Tx: '+document.getElementById('input').value);
    //document.getElementById('input').value = '';
}

function sentCommand(command){
    if(ws != null){
        ws.send(command);
    }
    log('Tx: '+command);
}

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
    if (mode != "manual") {
        options.shoulderFL = FL_leg.calcTheta1() * 180 / Math.PI;
        options.shoulderRL = FR_leg.calcTheta1() * 180 / Math.PI;
        options.shoulderFR = RL_leg.calcTheta1() * 180 / Math.PI;
        options.shoulderRR = RR_leg.calcTheta1() * 180 / Math.PI;
        options.kneeFL = FL_leg.calcTheta2() * 180 / Math.PI;
        options.kneeRL = FR_leg.calcTheta2() * 180 / Math.PI;
        options.kneeFR = RL_leg.calcTheta2() * 180 / Math.PI;
        options.kneeRR = RR_leg.calcTheta2() * 180 / Math.PI;
        options.hipFL = FL_leg.calcTheta3() * 180 / Math.PI;
        options.hipRL = FR_leg.calcTheta3() * 180 / Math.PI;
        options.hipFR = RL_leg.calcTheta3() * 180 / Math.PI;
        options.hipRR = RR_leg.calcTheta3() * 180 / Math.PI;
    }
}

function calcCommand(leg){
    cmd = "SERVO;"+leg.name+";"+ Math.round(leg.theta1 * 180 / Math.PI)+";"+ Math.round(leg.theta2 * 180 / Math.PI)+";"+ Math.round(leg.theta3 * 180 / Math.PI);
    //log(cmd);
    sentCommand(cmd);
}

function moveNext(leg, target_x, target_y, target_z) {
    let x, y, z, dx = 0, dy = 0, dz = 0;
    x = leg.X2;
    y = leg.Y2;
    z = leg.Z2;
    if (x < target_x) {
        if ((target_x - x) > DX) dx = DX;
        else dx = target_x - x;
    }
    else if (x > target_x) {
        if ((x - target_x) >= DX) dx = -DX;
        else dx = -(x - target_x);
    }
    //else console.log("x on target");
    if (y < target_y) {
        if ((target_y - y) > DY) dy = DY;
        else dy = target_y - y;
    }
    else if (y > target_y) {
        if ((y - target_y) >= DY) dy = -DY;
        else dy = -(y - target_y);
    }
    //else console.log("y on target");
    if (z < target_z) {
        if ((target_z - z) > DZ) dz = DZ;
        else dz = target_z - z;
    }
    else if (z > target_z) {
        if ((z - target_z) >= DZ) dz = -DZ;
        else dz = -(z - target_z);
    }
    //else console.log("z on target");
    if ((dx != 0) || (dy != 0) || (dz != 0)) {
        //console.log(x, y, target_x, target_y, dx, dy);
        leg.setTarget(x + dx, y + dy, z + dz);
        leg.calcInverseKinematics();
        calcCommand(leg);
    }
}

function moveNextAngle(leg, target_x, target_y, target_z) {
    let x, y, z, dx = 0, dy = 0, dz = 0;
    x = leg.theta1 * 180 / Math.PI; // shoulder
    y = leg.theta2 * 180 / Math.PI; // knee
    z = leg.theta3 * 180 / Math.PI; // hip
    //console.log(leg.name, x, y, z, target_x, target_y, target_z);
        
    if (x < target_x) {
        if ((target_x - x) > DX) dx = DX;
        else dx = target_x - x;
    }
    else if (x > target_x) {
        if ((x - target_x) >= DX) dx = -DX;
        else dx = -(x - target_x);
    }
    //else console.log("x on target");
    if (y < target_y) {
        if ((target_y - y) > DY) dy = DY;
        else dy = target_y - y;
    }
    else if (y > target_y) {
        if ((y - target_y) >= DY) dy = -DY;
        else dy = -(y - target_y);
    }
    //else console.log("y on target");
    if (z < target_z) {
        if ((target_z - z) > DZ) dz = DZ;
        else dz = target_z - z;
    }
    else if (z > target_z) {
        if ((z - target_z) >= DZ) dz = -DZ;
        else dz = -(z - target_z);
    }
    //else console.log("z on target");
    if ((dx != 0) || (dy != 0) || (dz != 0)) {
        //console.log(leg.name, x, y, z, target_x, target_y, target_z, dx, dy, dz);
        leg.setTheta1((x + dx) * Math.PI / 180);
        leg.setTheta2((y + dy) * Math.PI / 180);
        leg.setTheta3((z + dz) * Math.PI / 180);
        leg.calcForwardKinematics();
        calcCommand(leg);
    }
}

function sit() {
    moveNext(FL_leg, 0, 0, 0);
    moveNext(FR_leg, 0, 0, 0);
    moveNext(RL_leg, 0, 0, 0);
    moveNext(RR_leg, 0, 0, 0);
    if (SIM_2D == 1) drawRobot();
}

function stand() {
    moveNext(FL_leg, 0, 20, 0);
    moveNext(FR_leg, 0, 20, 0);
    moveNext(RL_leg, 0, 20, 0);
    moveNext(RR_leg, 0, 20, 0);
    if (SIM_2D == 1) drawRobot();
}

function manual() {
    // Todo: use variables instead of function for time improvement
    moveNextAngle(FL_leg, options.shoulderFL, options.kneeFL, options.hipFL);
    moveNextAngle(RL_leg, options.shoulderRL, options.kneeRL, options.hipRL);
    moveNextAngle(FR_leg, options.shoulderFR, options.kneeFR, options.hipFR);
    moveNextAngle(RR_leg, options.shoulderRR, options.kneeRR, options.hipRR);
    if (SIM_2D == 1) drawRobot();
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

    if (SIM_2D == 1) drawRobot();
}

// Position change (inverse kinematic)
function loop_2(step) {
    let x = 0;
    let y = step;
    let z = 0;
    // test inverse kinematics
    FL_leg.setTarget(x, y, z);
    FL_leg.calcInverseKinematics();

    FR_leg.setTarget(x, y, z);
    FR_leg.calcInverseKinematics();

    RL_leg.setTarget(x, y, z);
    RL_leg.calcInverseKinematics();

    RR_leg.setTarget(x, y, z);
    RR_leg.calcInverseKinematics();
    if (SIM_2D == 1) drawRobot();
    a1 += dir;
    if ((a1 == 30) || (a1 == 0)) dir = -dir;
}

function moveBezier(step) {
    let pos;
    pos = FL_leg.getBezierXY(a1 / 10);
    moveNext(FL_leg, pos.x, pos.y, 0);
    pos = FR_leg.getBezierXY(a1 / 10);
    moveNext(FR_leg, pos.x, pos.y, 0);
    pos = RL_leg.getBezierXY(a1 / 10);
    moveNext(RL_leg, pos.x, pos.y, 0);
    pos = RR_leg.getBezierXY(a1 / 10);
    moveNext(RR_leg, pos.x, pos.y, 0);
    if (SIM_2D == 1) drawRobot();
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

    if (SIM_2D == 1) drawRobot();
    a1 += dir;
    if ((a1 == 10) || (a1 == 0)) {
        dir = -dir;
        FL_leg.reversePath();
        FR_leg.reversePath();
        RL_leg.reversePath();
        RR_leg.reversePath();
    }
}

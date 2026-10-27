/*
_________Bartender Robot Arduino Code_________

The current setup has the base motor at X, first joint at Y, second joint at Z and the gripper joint at A

The servo (for the grippers) have been implimented.
Gear ratios have been implimented
Direction error was corrected

___HOW TO USE___

Send joint angles as a string in the serial input/output (TX pin on the raspbarry pi and RT pin on the Arduino).
Set the baud rate (of the raspbarry pi) to 115200
Send the signal with an interval between. eg the signal is sent every 30ms. (Sending the signal too fast can cause errors because the arduino buffer isnt too large but the code can be optimised to improve this)
At the moment the signal is just the angles with spaces in between like "30 75 310 180 0 0 0". First 4 are the stepper motors last 3 are for the servos


*/

#include <Servo.h>

Servo e;
Servo c;
Servo d;

int serv[4] = {90, 90, 90, 90};

int x = 2;
int y = 3;
int z = 4;
int a = 12;
int xdir = 5;
int ydir = 6;
int zdir = 7;
int adir = 13;

float xratio = (130.0/15.0);
float yratio = 60;
float zratio = 27.2;
float aratio = 32;

long m[4] = {0,0,0,0};
long b[4];
int n[4];
int interval[4] = {3000,3000,3000,3000}; // stores the delay between steps (the speed the motor needs)
unsigned long lastStep [4] = {0,0,0,0}; //the time the last step happened

int mCurr[4] = {0,0,0,0}; //current angle in steps
int move_s[4] = {0,0,0,0}; // how many steps still need to be made

int max = 900; //max speed of 300 rpm is 1 step per millisecond and 1 step per 1000 microseconds (currently set 100 microseconds faster)
int min = 2500; //min speed of 100 rpm is 1 step per 3 milliseconds and 1 step per 3000 microseconds (currently set 500 microseconds faster)

float slowT = 1000; // how many steps it takes to slow down (values below 1000 are unstable for some reason)
float fastT = 900; // how many steps it takes to get to max speed from min
String input = "";

void setup() {
  // put your setup code here, to run once:
e.attach(9);
c.attach(10);
d.attach(11);

pinMode(x,OUTPUT);
digitalWrite(x, LOW);
pinMode(xdir,OUTPUT);
digitalWrite(xdir, LOW);

pinMode(y,OUTPUT);
digitalWrite(y, LOW);
pinMode(ydir,OUTPUT);
digitalWrite(ydir, LOW);

pinMode(z,OUTPUT);
digitalWrite(z, LOW);
pinMode(zdir,OUTPUT);
digitalWrite(zdir, LOW);

pinMode(a,OUTPUT);
digitalWrite(a, LOW);
pinMode(adir,OUTPUT);
digitalWrite(adir, LOW);

Serial.begin(115200);
m[0] = 0;
m[1] = 0;
m[2] = 0;
m[3] = 0;
}
void normalizer(long m[4], long (&b)[4]){

  for (int i = 0; i < 4; i++){
     b[i] = m[i]*200 / 360;
  }
}


void loop() {
  // put your main code here, to run repeatedly:


readSerial(m, xratio, yratio, zratio, aratio, serv);
e.write(serv[0]);
c.write(serv[1]);
d.write(serv[2]);
normalizer(m,b);
for(int i = 0; i<4; i++){
  n[i] = b[i];
}
ramper(interval, mCurr, n, move_s, slowT, fastT);
if (move_s[0] != 0 || move_s[1] != 0 || move_s[2] != 0 || move_s[3] != 0){
move(interval, move_s, lastStep, mCurr);
}

}




void ramper(int (&interval)[4], int mCurr[4], int n[4], int (&move_s)[4], int stopT, int fastT){
  for (int i = 0; i < 4; i++){// checking how many steps are still needed
    move_s[i] = n[i] - mCurr[i];
      // Serial.print(" n[i]: ");
      // Serial.println(n[i]);
      // Serial.print(" mCurr[i]: ");
      // Serial.println(mCurr[i]);
  }



  for (int i = 0; i < 4; i++){
    if (abs(move_s[i])< stopT/(min/1000)){ // check if we should speed ramp or slow down (true means slow down)
    //     interval[i] += (min - interval[i])/(abs(move_s[i])); // step down speed till min

    if (interval[i]+((min - max)/slowT)<=min){//check if we are going to exede max
        interval[i] += (min - max)/slowT;// add incriment to interval
    }
    }else{
      if (interval[i]-((min - max)/fastT)>=max){//check if we are going to exede max
        interval[i] -= (min - max)/fastT;// add incriment to interval
      }
    }
  }
}




void move(int interval[4], int move_s[4], unsigned long (&lastStep)[4], int (&mCurr)[4]){
  if (move_s[0]<0){
    digitalWrite(xdir, HIGH);
  }else{
    digitalWrite(xdir, LOW);
  }

  if (move_s[1]<0){
    digitalWrite(ydir, HIGH);
  }else{
    digitalWrite(ydir, LOW);
  }

  if (move_s[2]<0){
    digitalWrite(zdir, HIGH);
  }else{
    digitalWrite(zdir, LOW);
  }

  if (move_s[3]<0){
    digitalWrite(adir, HIGH);
  }else{
    digitalWrite(adir, LOW);
  }


  for(int i = 0; i < 4; i++){
      // if (move_s[i]<0){
      // // Serial.print(" move_s[i]: ");
      // // Serial.println(move_s[i]);
      // digitalWrite(adir, HIGH);
      // }else{
      // digitalWrite(adir, LOW);
      // }

    if ((micros()-lastStep[i])>interval[i]){
      if (abs(move_s[i])>0){
        step(findM(i));
        lastStep[i] = micros();

        
        if (move_s[i]<=0){
          mCurr[i] -= 1;
        }else{
          mCurr[i] += 1;
        }
        

      }
      
    }
  }
}

void step(int M){
digitalWrite(M, HIGH);
delayMicroseconds(2);
digitalWrite(M, LOW);
}

int findM(int i){
  if(i==0){
    return x;
  }else if (i==1){
    return y;
  }else if (i==2){
    return z;
  }else{
    return a;
  }
}
/*
float abs(float n){
  if (n<0){
    n = -n;
  }
  return n
}
*/
int set_to_min(int x[4]){
  for (int i = 0; i < 4; i++){
    x[i] = min;
  }
}

int set_to_max(int x[4]){
  for (int i = 0; i < 4; i++){
    x[i] = max;
  }
}

// void readSerial(long (&m)[4] ){
  
//   if (Serial.available() > 0){
//     input = Serial.readStringUntil('\n');
//     Serial.print("I see: ");
//     Serial.println(input);
//     int h = 0;
//     String first = "";
//     while (input[h] != ' '){
//       first = first + input[h];
//       h++; 
//     }
//     String second = "";
//     h++;
//     while (input[h] != ' '){
//       second = second + input[h];
//       h++; 
//     }
    
//     String third = "";
//     h++;
//     while (input[h] != ' '){
//       third = third + input[h];
//       h++; 
//     }
//     h++;
//     String fourth = "";
//     while (input[h] != ' '){
//       fourth = fourth + input[h];
//       h++; 
//     }
    
//     m[0] = first.toInt();
//     m[1] = second.toInt();
//     m[2] = third.toInt();
//     m[3] = fourth.toInt();
//   }
// }

void readSerial(long (&m)[4], float x, float y, float z, float a, int (&serv) [4] ){
  
  if (Serial.available() > 0){
    String input = Serial.readStringUntil('\n');
    char input2[30];
    input.toCharArray(input2,sizeof(input2));

    char* first = strtok(input2," ");

    char* second = strtok(NULL, " ");
    
    char* third = strtok(NULL, " ");
    
    char* fourth = strtok(NULL, " ");

    serv[0] = atoi(strtok(NULL, " "));

    serv[1] = atoi(strtok(NULL, " "));

    serv[2] = atoi(strtok(NULL, " "));

    
    m[0] = atoi(first)*x;
    m[1] = atoi(second)*y;
    m[2] = atoi(third)*z;
    m[3] = atoi(fourth)*a;

  }
}

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Effects
import Qt5Compat.GraphicalEffects

ApplicationWindow {
    id: appWin 
    visible: true
    width:1024
    height: 600 
    title: "Menu"
    flags: Qt.FramelessWindowHint | Qt.Window
    visibility: Window.FullScreen

    property QtObject backend
    property var fullMenu:[]
    property var orderMenu: []
    property int currentItem: 0

    //order selection
    property bool isOrdering: false
    property int selectedSide: 0 //1 = left img & 2 = right img or drink clicked
    property bool isBusy: false

    RowLayout {
        anchors.fill: parent
        anchors.margins:10
        spacing: 20

        //col 1/ <
        Rectangle {
            opacity: isOrdering ? 0:1
            Layout.preferredWidth: 80
            Layout.fillHeight: true
            color: "transparent"

            Text {
                anchors.centerIn: parent
                text: "<"
                font.pixelSize: 64
                color: "black"
            }

            //touch visual feedback
            Rectangle {
                anchors.fill: parent
                color: "black"
                opacity: 0.4
                visible: lArrowMouse.pressed
                z:1
            }

            //WHAT HAPPENS WHEN CLICKED
            MouseArea {
                id: lArrowMouse
                z:2
                anchors.fill: parent
                enabled: !isOrdering
                onClicked: {
                    console.log("Left arrow clicked")
                    if (fullMenu.length>0) {
                        currentItem = (currentItem - 1 + fullMenu.length) %fullMenu.length
                    }
                }
            }
        }

        //col 2 (LEFT)
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            //drink card
            Rectangle {
                id: cardA
                anchors.fill: parent
                radius: 15
                color: "black"

                //only if not ordering OR selected
                visible: !isOrdering || selectedSide==1

                Image {
                    id: imgA
                    anchors.fill: parent
                    fillMode: Image.PreserveAspectCrop
                    source: fullMenu.length > 0? "./Images/" + fullMenu[currentItem]: ""
                    visible: false
                }

                //Rounded corners
                OpacityMask {
                    anchors.fill : imgA
                    source: imgA
                    maskSource: cardA
                }

                //touch visual feedback
                Rectangle {
                    anchors.fill: parent
                    color: "black"
                    opacity: 0.4
                    visible: cardAMouse.pressed
                    z:1
                }

                //WHAT HAPPENS WHEN CLICKED
                MouseArea {
                    id: cardAMouse
                    z:2
                    anchors.fill: parent
                    onClicked: {
                        if (!isOrdering){
                            console.log("drink A clicked")
                            isOrdering=true
                            selectedSide = 1
                        }//end if not ordering
                    }//end mouseclick event
                }
            }

            //ORDER PANEL for imgB/RHS drink
            Rectangle {
                id: orderA
                anchors.fill: parent
                radius: 15
                color: "white"
                visible: isOrdering && selectedSide==2
                clip: true

                // Order background img
                Image {
                    id: imgAOrder
                    anchors.fill: parent
                    fillMode: Image.PreserveAspectCrop
                    source: orderMenu.length > 0 ? "./Images/" + orderMenu[(currentItem+1)% orderMenu.length]: ""
                    visible: false
                }

                //Rounded corners
                OpacityMask {
                    anchors.fill : imgAOrder
                    source: imgAOrder
                    maskSource: orderA
                }

                //ORDER & CANCEL SECTION
                Column {
                    anchors.centerIn: parent
                    spacing: 20
                    
                    //ORDER BUTTON for drink B
                    Rectangle {
                        id: orderBbtn
                        width: 180
                        height: 60
                        radius: 30
                        color: "#4CAF50"
                        z:3

                        Text{
                            anchors.centerIn: parent
                            text: "ORDER"
                            font.pixelSize: 25
                            font.bold : true
                            color: "white"
                        }

                        //touch visual feedback
                        Rectangle {
                            anchors.fill: parent
                            color: "black"
                            opacity: 0.4
                            visible: orderBMouse.pressed
                            radius: 30
                            z:4
                        }

                        MouseArea{
                            id: orderBMouse
                            z: 5
                            anchors.fill: parent
                            onClicked: {
                                console.log("MOTORS MOVING for Drink B")
                                isOrdering = false
                                selectedSide = 0

                                isBusy=true
                                backend.startPour()
                            }
                        }
                    }//end order btn 
                    

                    // RED CANCEL Btn for drink B
                    Rectangle {
                        width: 180
                        height: 60
                        radius: 30
                        color: "#F44336"

                        Text{
                            anchors.centerIn: parent
                            text: "CANCEL"
                            font.pixelSize: 25
                            font.bold : true
                            color: "white"
                        }

                        //touch visual feedback
                        Rectangle {
                            anchors.fill: parent
                            color: "black"
                            opacity: 0.4
                            visible: cancelBMouse.pressed
                            radius: 30
                            z:1
                        }

                        MouseArea{
                            id: cancelBMouse
                            z: 2
                            anchors.fill: parent
                            onClicked: {
                                console.log("CANCEL ORDER for Drink B")
                                isOrdering = false
                                selectedSide = 0
                            }
                        }
                    }//end cancel btn
                }
            }
        }//end column 2

        //col3 
        Item { 
            Layout.fillWidth: true
            Layout.fillHeight: true

            //drink card
            Rectangle {
                id: cardB
                anchors.fill: parent
                radius: 15
                color: "black"

                //only if not ordering OR selected
                visible: !isOrdering || selectedSide==2

                Image {
                    id: imgB
                    anchors.fill: parent
                    fillMode: Image.PreserveAspectCrop
                    source: fullMenu.length > 0? "./Images/" + fullMenu[(currentItem+1) % fullMenu.length]: ""
                    visible: false
                }

                //Rounded corners
                OpacityMask {
                    anchors.fill : imgB
                    source: imgB
                    maskSource: cardB
                }

                //touch visual feedback
                Rectangle {
                    anchors.fill: parent
                    color: "black"
                    opacity: 0.4
                    visible: cardBMouse.pressed
                    z:1
                }

                //WHAT HAPPENS WHEN CLICKED
                MouseArea {
                    id: cardBMouse
                    z: 2
                    anchors.fill: parent
                    onClicked: {
                        if (!isOrdering){
                            console.log("Drink B clicked")
                            isOrdering=true
                            selectedSide = 2
                        }//end if not ordering
                    }//end mouseclicked
                }
            }
            

            //ORDER PANEL for imgA/LHS drink
            Rectangle {
                id: orderB
                anchors.fill: parent
                radius: 15
                color: "white"
                visible: isOrdering && selectedSide==1
                clip: true

                // order bg img
                Image {
                    id: imgBOrder
                    anchors.fill: parent
                    fillMode: Image.PreserveAspectCrop
                    source: orderMenu.length > 0 ? "./Images/" + orderMenu[(currentItem)% orderMenu.length]: ""
                    visible: false
                }

                //Rounded corners
                OpacityMask {
                    anchors.fill : imgBOrder
                    source: imgBOrder
                    maskSource: orderB
                }

                //ORDER & CANCEL SECTION
                Column {
                    anchors.centerIn: parent
                    spacing: 20


                    //ORDER BUTTON for drink A
                    Rectangle {
                        width: 180
                        height: 60
                        radius: 30
                        color: "#4CAF50"


                        Text{
                            anchors.centerIn: parent
                            text: "ORDER"
                            font.pixelSize: 25
                            font.bold : true
                            color: "white"
                        }

                        //touch visual feedback
                        Rectangle {
                            anchors.fill: parent
                            color: "black"
                            opacity: 0.4
                            visible: orderBMouse.pressed
                            radius: 30
                            z:3
                        }

                        MouseArea{
                            id: orderAMouse
                            z: 4
                            anchors.fill: parent
                            onClicked: {
                                console.log("MOTORS MOVING for Drink A")
                                isOrdering = false
                                selectedSide = 0

                                isBusy=true
                                backend.startPour()
                            }
                        }
                    } //end order btn

                    // RED CANCEL Btn for drink A
                    Rectangle {
                        width: 180
                        height: 60
                        radius: 30
                        color: "#F44336"

                        Text{
                            anchors.centerIn: parent
                            text: "CANCEL"
                            font.pixelSize: 25
                            font.bold : true
                            color: "white"
                        }

                        //touch visual feedback
                        Rectangle {
                            anchors.fill: parent
                            color: "black"
                            opacity: 0.4
                            visible: cancelAMouse.pressed
                            radius: 30
                            z:1
                        }

                        MouseArea{
                            id: cancelAMouse
                            z: 2
                            anchors.fill: parent
                            onClicked: {
                                console.log("CANCEL ORDER for Drink A")
                                isOrdering = false
                                selectedSide = 0
                            }
                        }
                    }//end cancel btn
                }
            }
        }

        //col 4/ >
        Rectangle {
            opacity: isOrdering ? 0:1
            Layout.preferredWidth: 80
            Layout.fillHeight: true
            color: "transparent"

            Text {
                anchors.centerIn: parent
                text: ">"
                font.pixelSize: 64
                color: "black"
            }

            //touch visual feedback
            Rectangle {
                anchors.fill: parent
                color: "black"
                opacity: 0.4
                visible: rArrowMouse.pressed
                z:1
            }

            //WHAT HAPPENS WHEN CLICKED
            MouseArea {
                id: rArrowMouse
                z:2
                anchors.fill: parent
                enabled: !isOrdering
                onClicked: {
                    console.log("Right arrow clicked")
                    if (fullMenu.length>0){
                        currentItem = (currentItem+1)%fullMenu.length
                    }
                }
            }
        }

    }

    //WHILE ORDERING
    Rectangle{
        anchors.fill: parent
        color: "#CC000000"
        visible: isBusy
        z: 99

        MouseArea {
            anchors.fill: parent
        }

        Text{
            anchors.centerIn: parent
            text: "Preparing your drink...\n\nPlease keep clear of the arm!"
            color: "white"
            font.pixelSize: 50
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
        }
    }

    //Kiosk Mode Escape
    Rectangle{
        //top left corner
        width: 100
        height: 100
        anchors.top: parent.top
        anchors.left: parent.left
        z:100 // above EVERYTHING
        color: "transparent"

        MouseArea{
            anchors.fill: parent

            //close by holding for 5sec
            pressAndHoldInterval: 5000
            onPressAndHold: {
                console.log("Escaping Kiosk-Mode. Shutting Down GUI...")
                Qt.quit()
            }
        }
    }

    Connections{
        target: backend

        //get drinks list
        function onUpdatedDrinks(drinkMenu, orderList) {
            fullMenu = drinkMenu
            orderMenu = orderList
            console.log("QML received drinks and order bg")
        }

        //waits for arm not busy/stationary/emit
        function onArmReady() {
            isBusy=false
            isOrdering=false
            selectedSide=0
            console.log("QML unlocked for next order")
        }
    }
}
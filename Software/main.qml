import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Effects
import Qt5Compat.GraphicalEffects
import QtMultimedia

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

    //loading screens
    property var videoMenu:[]
    property var nextOrderMenu: []
    property string activeVideo:""
    property string activeNextOrder: ""
    

    //order selection
    property bool isOrdering: false
    property int selectedSide: 0 //1 = left img & 2 = right img or drink clicked
    property bool isBusy: false
    property bool showNextOrder: false

    ListModel{
        id: drinkModel
        ListElement{
            name: "Blueberry Bliss"
            icon: "./Images/DrinkB.png"
        }
        ListElement{
            name: "Passionfruit Paradise"
            icon: "./Images/DrinkP.png"
        }
        ListElement{
            name: "Watermelon Wonder"
            icon: "./Images/DrinkW.png"
        }
    }//end drink card list

    Component{
        id: carouselDelegate

        Item {
            id: wrapper
            width: 320
            height: 420

            //make only center drink opaque and larger
            opacity: PathView.isCurrentItem? 1: 0.3
            //scale: PathView.isCurrentItem ? 1 : 0.8

            //ANIMATE SMOOTHER!!
            Behavior on opacity {
                NumberAnimation{duration:250}
            }//end animation

            Column{
                anchors.fill: parent
                Item {
                    anchors.horizontalCenter: parent.horizontalCenter
                    width: 320
                    height: 420

                    Image { 
                        id: imgRaw
                        anchors.fill: parent
                        source: icon
                        fillMode: Image.PreserveAspectCrop
                        visible: false
                    }//end img

                    OpacityMask{
                        anchors.fill: parent
                        source: imgRaw
                        maskSource: Rectangle{
                            width: 320
                            height: 420
                            radius: 15
                        }
                    }//end making rounded corners

                    //add border 
                    Rectangle{
                        anchors.fill: parent
                        radius:15
                        color: "transparent"

                        border.color: wrapper.PathView.isCurrentItem? "#7e7e7e": "transparent"
                        border.width:4

                        //fade border out when not selected
                        Behavior on border.color{
                            ColorAnimation{duration:250}
                        }//end animation
                    }//end border 
                }//end grouped item 
            }
            //WHAT HAPPENS WHEN CLICKED
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    if (wrapper.PathView.isCurrentItem){
                        console.log("Starting order for"+ wrapper.drinkName)
                        activeVideo = "./Images/"+ videoMenu[index]
                        activeNextOrder = "./Images/"+nextOrderMenu[index]

                        isBusy = true
                        showNextOrder=false
                        backend.startPour(index)
                    } else {
                        //if not centered drink 
                        swipeCarousel.currentIndex=index
                    }
                }
            }
        }        
    }

    PathView{
        id: swipeCarousel
        anchors.fill: parent

        //link to menu
        model: drinkModel
        delegate: carouselDelegate

        pathItemCount: 3
        //center active drink
        preferredHighlightBegin: 0.5
        preferredHighlightEnd: 0.5

        highlightRangeMode: PathView.StrictlyEnforceRange
        snapMode: PathView.SnapToItem

        path: Path{
            startX:0
            startY: swipeCarousel.height/2

            PathLine{
                x: swipeCarousel.width
                y: swipeCarousel.height/2
            }
        }
    }//end path view

    PageIndicator {
        anchors.bottom: swipeCarousel.bottom
        anchors.bottomMargin: 30
        anchors.horizontalCenter: parent.horizontalCenter

        count: swipeCarousel.count
        currentIndex: swipeCarousel.currentIndex

        delegate: Rectangle{
            width:12
            height: 12
            radius:6
            color: index === swipeCarousel.currentIndex? "#3c3d3c" : "#acacac"

            Behavior on color {
                ColorAnimation{duration:250}
            }//end animation
        }
    }//end page circle indicators


    //WHILE ORDERING: POURING SCREEN VIDEO
    Rectangle{
        id: pouringScreen
        anchors.fill: parent
        color: "#CC000000"
        visible: isBusy
        z: 90

        MediaPlayer {
            id: pouringPlayer
            source: activeVideo
            loops: MediaPlayer.Infinite
            videoOutput: pouringVideo
        }

        VideoOutput{ 
            id: pouringVideo
            anchors.fill: parent
            fillMode: VideoOutput.PreserveAspectCrop
        }

        //Auto play/stop
        onVisibleChanged: {
            if (visible){
                pouringPlayer.play()
            } else {
                pouringPlayer.stop()
            }
        }
    }

    //Next Order SCREEN
    Rectangle{
        id: completedOrderScreen
        anchors.fill: parent
        visible: showNextOrder
        z: 90

        Image{
            anchors.fill: parent
            source: activeNextOrder
            fillMode: Image.PreserveAspectCrop

            //NEXT ORDER BUTTON 
            Rectangle {
                id: nextOrderbtn
                width: 200
                height: 60
                radius: 30
                color: "#4CAF50"
                z:95

                anchors.centerIn: parent
                anchors.verticalCenterOffset: 80
                anchors.horizontalCenterOffset: -245

                //DROPSHADOW!!
                layer.enabled:true
                layer.effect: MultiEffect {
                    shadowEnabled: true
                    shadowColor: "#1d401e"
                    shadowVerticalOffset: 6
                    shadowBlur: 0.8
                }

                Text{
                    anchors.centerIn: parent
                    text: "NEXT ORDER"
                    font.pixelSize: 22
                    font.bold : true
                    color: "white"
                }

                //touch visual feedback
                Rectangle {
                    anchors.fill: parent
                    color: "black"
                    opacity: 0.4
                    visible: nextOrderMouse.pressed
                    radius: 30
                    z:4
                }

                MouseArea{
                    id: nextOrderMouse
                    z: 96
                    anchors.fill: parent
                    onClicked: {
                        showNextOrder = false
                    }
                }
            }//end next order btn
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
        function onUpdatedDrinks(drinkList, orderList, videoList, nextOrderList) {
            fullMenu = drinkList
            orderMenu = orderList
            videoMenu = videoList
            nextOrderMenu = nextOrderList

            console.log("QML received all menus and videos")
        }

        //waits for arm not busy/stationary/emit
        function onArmReady() {
            isBusy = false
            isOrdering=false
            selectedSide=0
            showNextOrder = true
            console.log("QML unlocked for next order")
        }
    }
}
def zoom_to_scale(event, scale):
    print(event.key())
    # check if Ctrl is held
    # if event.modifiers() & Qt.ControlModifier:
    #     # check if Y is pressed
    #     print("")
    #     if event.key() == Qt.Key_W:
    #         iface.mapCanvas().zoomScale(scale)
                    
con = iface.mainWindow().keyPressed.connect(lambda event: zoom_to_scale(event, 1000))


# to disconnect (and halt the behaviour)
#iface.mapCanvas().keyPressed.disconnect(con)


class SelectZoneWidget(QtGui.QWidget):

    _imageChanged = pyqtSignal(np.ndarray)
    _imageReset = pyqtSignal()
    _homographyChanged = pyqtSignal(list)

    def __init__(self, hWidget, parent=None):
        super(SelectZoneWidget, self).__init__(parent)
        self._hWidget = hWidget
        self._imageChanged.connect(self._hWidget.setImage)
        self._homographyChanged.connect(self._hWidget.setHomography)
        self._imageReset.connect(self._hWidget.reset)
        self._initUI()

    # Initialize the UI
    def _initUI(self):
        # Widget parameters
        self.setMinimumWidth(300)

        # Create the figure
        self._fig = Figure()

        # Canvas configuration
        self._canvas = FigureCanvas(self._fig)
        self._canvas.setParent(self)
        self._canvas.mpl_connect('button_press_event', self._onPick)

        # Plot configuration
        self._plt = self._fig.add_subplot(111)
        self._plt.xaxis.set_visible(False)
        self._plt.yaxis.set_visible(False)

        # Finalize figure
        self._fig.subplots_adjust(wspace=0, hspace=0)

        # Reset the variables
        self.reset()

        # Create the layout
        vbox = QtGui.QVBoxLayout()

        # Add Canvas to the layout
        vbox.addWidget(self._canvas)

        # Set the layout
        self.setLayout(vbox)

        zp = ZoomPan()
        figZoom = zp.zoom_factory(self._plt)
        figPan = zp.pan_factory(self._plt)


    # Reset the variables to original state
    def reset(self):
        self._canvas.hide()
        self._image = None
        self._points = []
        self._imageReset.emit()

    # Set an image to the widget
    def setImage(self, image):
        self.reset()
        self._image = image
        self._redraw()
        self._canvas.show()
        self._imageChanged.emit(image)

    # Get the image of the widget
    def getImage(self):
        pass

    # Redraw the image and points
    def _redraw(self):
        # Clear the canvas
        self._plt.clear()

        # Plot the image
        if self._image is not None:
            self._plt.autoscale(True)
            self._plt.imshow(self._image)
            self._plt.autoscale(False)

        # Plot the points
        if len(self._points) > 0:
            xs = [x for (x, _) in self._points]
            ys = [y for (_, y) in self._points]
            self._plt.plot(xs + [xs[0]], ys + [ys[0]], '-', color='red')
            self._plt.plot(xs + [xs[0]], ys + [ys[0]], 'o', color='blue')

        # Draw the canvas
        self._canvas.draw()

    # Handle click events
    def _onPick(self, event):

        if event.button == 3:
            self._redraw()
        elif event.button != 1:
            return

        # Get point position
        x = event.xdata
        y = event.ydata

        if x is None or y is None:
            return

        # For each existing points
        for px, py in self._points:

            # Compute distance to current point
            dst = np.sqrt((px - x) ** 2 + (py - y) ** 2)

            # If the distance is small remove it
            if dst < 10:
                self._removePoint(px, py)
                self._redraw()
                return

        # Delegate to add the point
        self._addPoint(x, y)

        # Redraw the image
        self._redraw()

    # Add a new point
    def _addPoint(self, x, y):
        # Count points
        n = len(self._points)

        # If less than 3 points just add it
        if n < 3:
            self._points.append((x, y))
            return

        # If already 4 points, ignore it
        if n >= 4:
            return

        # Else a verification must be done
        if self._validPoint(x, y):
            # Add the point
            self._points.append((x, y))

            # Reorder points to have consistant rectangle when drawing
            self._reorderPoints()

            # Lunch the homography
            self._homographyChanged.emit(self._points)

    # Remove an existing point
    def _removePoint(self, x, y):
        # Reset homograpy if we remove the 4th point
        if len(self._points) == 4:
            self._imageChanged.emit(self._image)

        # Remove the point
        self._points = list(filter(lambda v: v != (x, y), self._points))

    # Reorder points to have a planar graph (meaning no line crossing)
    def _reorderPoints(self):
        # List of reordoned points
        ordPoints = [self._points[0]]

        # List of selectionnable points
        others = self._points[1:]

        # Fill reordoned points
        while len(ordPoints) < 4:
            # Previous point
            p = ordPoints[-1]

            # Test other points
            for pn in others:
                # Points to verify side
                verify = list(filter(lambda v: v != pn and v != p,
                                     self._points))

                # Verify side
                if allSameSide(p, pn, verify):
                    ordPoints.append(pn)
                    others = list(filter(lambda v: v != pn, others))
                    break

        # Set the reordoned points
        self._points = ordPoints

    def _validPoint(self, x, y):
        a = [p for p in self._points] + [(x, y)]
        triangles = [[a[0], a[1], a[2]], [a[0], a[1], a[3]],
                     [a[0], a[2], a[3]], [a[1], a[2], a[3]]]
        points = [a[3], a[2], a[1], a[0]]

        for triangle, point in zip(triangles, points):
            px, py = point
            if lieIntoTriangle(triangle, px, py):
                return False

        return True
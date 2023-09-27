import dateutil.parser
import geojson
from PythonCoordinates.coordinates.geospatial_coordinates import SourcePoint, CartesianCoordinate
from PythonCoordinates.measurables.physical_quantities import Length, Angle, Speed
import numpy as np
import pandas as pd


class Track:
    """
    This class will use a series of SourcePoint objects to create a MultiPoint GeoJson object. This object will hold
    the additional information from the SourcePoint in the properties element of the individual Point objects.
    """

    def __init__(self, a=None, columns=None):
        """
        This constructor permits the creation of the MultiPoint object through the use of a string, or an Array that
        contains the information that we want to create a Track from.
        :param a:
            This is either a string, in which case the data is read from a file, or a Numpy.ndarray, in which case
            the collection of Points is created from the elements of the array
        :param columns:
            In the case where the input is a DataFrame, we need to understand how to parse the columns of the
            DataFrame to extract the information that we want to create the track from
        """

        self._points = None

        if isinstance(a, str):
            self._read_file(a)
        elif isinstance(a, np.ndarray):
            self._build_from_array(a)
        elif isinstance(a, pd.DataFrame) and columns is not None:
            self._build_from_dataframe(a, columns)

    def _read_file(self, a: str):
        """
        Since the constructor determined that the use provided a string, it is assumed that the string represents a
        path to a file that we want to load. This function will load the data into the interface.
        :param a:
            The string that represents a path to the file containing the information that we want to read
        """
        import os.path
        from geojson import FeatureCollection

        if not os.path.exists(a):
            raise FileNotFoundError(
                "The interface expected a file with the GeoJson data, but the string does not "
                "lead to a file"
            )
        with open(a, 'r') as file:
            data = geojson.load(file)

        self._points = np.empty((len(data['features']),), dtype=SourcePoint)
        n = 0

        for pt in data['features']:
            self._points[n] = SourcePoint(
                CartesianCoordinate(
                    Length(pt['geometry']['coordinates'][0]),
                    Length(pt['geometry']['coordinates'][1]),
                    Length(pt['geometry']['coordinates'][2])
                    )
                )
            self._points[n].heading = Angle(pt['properties']['heading'])
            self._points[n].pitch = Angle(pt['properties']['pitch'])
            self._points[n].roll = Angle(pt['properties']['roll'])
            if isinstance(pt['properties']['time'], float):
                self._points[n].time = pt['properties']['time']
            else:
                self._points[n].time = dateutil.parser.parse(pt['properties']['time'])

            n += 1

    def _build_from_array(self, a: np.ndarray):
        """
        In the constructor the argument was an array, so we need to determine whether the array is a collection of
        SourcePoint objects. If it is, we can create an instance of the MultiPoint object and populate it with the
        information from the SourcePoint.
        :param a:
            The array of source point objects that we will use to create the MultiPoint object.
        """

        if not isinstance(a[0], SourcePoint):
            raise ValueError("It was expected that the array contain elements of type SourcePoint.")

    def _build_from_dataframe(self, a: pd.DataFrame, columns: dict):
        """
        This function will take the data from the DataFrame object and attempt to construct the information within a
        SourcePoint from each row of data.
        :param a:
            The DataFrame containing the information
        :param columns:
            A np.ndarray that contains the names of the columns in the order that we want to extract data
        """
        import datetime

        #   Check to make sure that at least the location information is provided within the dictionary
        if not Track._check_columns(columns):
            raise ValueError("We raise a value error here for completeness of the code, but it will never get here")

        #   Build the array that will hold the SourcePoint objects
        self._points = np.empty(shape=(a.shape[0],), dtype=SourcePoint)

        #   Create a set of objects representing the information in the DataFrame, converted to the correct object
        #   and units
        latitude = a[columns['latitude']]
        longitude = a[columns['longitude']]
        altitude = self._extract_altitude(a, columns)
        heading = self._extract_heading(a, columns)
        pitch = self._extract_pitch(a, columns)
        roll = self._extract_roll(a, columns)
        times = self._extract_times(a, columns)

        #   Now loop through the rows of the DataFrame and convert the data to the correct units and objects to
        #   create the SourcePoint object
        for i in range(a.shape[0]):
            self.points[i] = SourcePoint(latitude[i],
                                         longitude[i],
                                         altitude[i],
                                         heading[i],
                                         pitch[i],
                                         roll[i],
                                         Speed(),
                                         times[i])

    @staticmethod
    def _extract_times(a: pd.DataFrame, columns: dict):
        """
        AS with other elements of the data, the heading can be represented as a degree or radian value. This will
        determine which units to use for the creation of the heading.
        :param a:
            The DataFrame that has the information for the points
        :param columns:
            A collection of column names and the values that we expect within the Track object
        :return:
            The Pandas.Series that represents the column of heading values
        """
        import dateutil.parser
        import datetime

        if not (('time' in columns.keys()) or ('tpm' in columns.keys())):
            raise ValueError("The heading was not discovered in the collection of column definitions")

        if 'time' in columns.keys():
            np_dt = a[columns['time']].values.astype(dtype='datetime64[ms]')
            times = np.empty((len(np_dt),), dtype=datetime.datetime)
            for i in range(len(times)):
                times[i] = np_dt[i].astype(datetime.datetime)
            return times
        else:
            return a[columns['tpm']]

    @staticmethod
    def _extract_heading(a: pd.DataFrame, columns: dict):
        """
        AS with other elements of the data, the heading can be represented as a degree or radian value. This will
        determine which units to use for the creation of the heading.
        :param a:
            The DataFrame that has the information for the points
        :param columns:
            A collection of column names and the values that we expect within the Track object
        :return:
            The Pandas.Series that represents the column of heading values
        """

        if not (('heading_deg' in columns.keys()) or ('heading_rad' in columns.keys())):
            raise ValueError("The heading was not discovered in the collection of column definitions")

        if 'heading_deg' in columns.keys():
            angle_units = Angle.Units.Degrees
            column_name = 'heading_deg'
        else:
            angle_units = Angle.Units.Radians
            column_name = 'heading_rad'

        angle = np.empty(shape=(a.shape[0],), dtype=Angle)
        values = np.asarray(a[columns[column_name]])

        for i in range(a.shape[0]):
            angle[i] = Angle(values[i], angle_units)

        return angle

    @staticmethod
    def _extract_pitch(a: pd.DataFrame, columns: dict):
        """
        AS with other elements of the data, the heading can be represented as a degree or radian value. This will
        determine which units to use for the creation of the heading.
        :param a:
            The DataFrame that has the information for the points
        :param columns:
            A collection of column names and the values that we expect within the Track object
        :return:
            The Pandas.Series that represents the column of heading values
        """

        if not (('pitch_deg' in columns.keys()) or ('pitch_rad' in columns.keys())):
            raise ValueError("The pitch was not discovered in the collection of column definitions")

        if 'pitch_deg' in columns.keys():
            angle_units = Angle.Units.Degrees
            column_name = 'pitch_deg'
        else:
            angle_units = Angle.Units.Radians
            column_name = 'pitch_rad'

        angle = np.empty(shape=(a.shape[0],), dtype=Angle)
        values = np.asarray(a[columns[column_name]])

        for i in range(a.shape[0]):
            angle[i] = Angle(values[i], angle_units)

        return angle

    @staticmethod
    def _extract_roll(a: pd.DataFrame, columns: dict):
        """
        AS with other elements of the data, the heading can be represented as a degree or radian value. This will
        determine which units to use for the creation of the heading.
        :param a:
            The DataFrame that has the information for the points
        :param columns:
            A collection of column names and the values that we expect within the Track object
        :return:
            The Pandas.Series that represents the column of heading values
        """

        if not (('roll_deg' in columns.keys()) or ('roll_rad' in columns.keys())):
            raise ValueError("The roll was not discovered in the collection of column definitions")

        if 'roll_deg' in columns.keys():
            angle_units = Angle.Units.Degrees
            column_name = 'roll_deg'
        else:
            angle_units = Angle.Units.Radians
            column_name = 'roll_rad'

        angle = np.empty(shape=(a.shape[0],), dtype=Angle)
        values = np.asarray(a[columns[column_name]])

        for i in range(a.shape[0]):
            angle[i] = Angle(values[i], angle_units)

        return angle

    @staticmethod
    def _extract_altitude(a: pd.DataFrame, columns: dict):
        """
        Since there are multiple ways to represent the altitude, we need to build methods for altering the units and
        returning an array of length objects
        :param a:
            The DataFrame that holds the information for the flight track
        :param columns:
            The dictionary that contains the column definitions
        :return:
            ndarray of Length objects that will hold the data for the altitude of the object
        :raises:
            ValueError if the dictionary contains altitude descriptions that are mean sea level rather than above
            ground level
        """

        if ('altitude_m_msl' in columns.keys()) or ('altitude_ft_msl' in columns.keys()):
            raise ValueError("There is no method for conversion of Mean Sea Level to Above Ground Level at this point")

        if 'altitude_ft_agl' in columns.keys():
            altitude_units = Length.Units.Feet
            column_name = 'altitude_ft_agl'
        else:
            altitude_units = Length.Units.Meters
            column_name = 'altitude_m_agl'

        altitude = np.empty(shape=(a.shape[0],), dtype=Length)
        values = np.asarray(a[columns[column_name]])

        for i in range(a.shape[0]):
            altitude[i] = Length(values[i], altitude_units)

        return altitude

    @staticmethod
    def _check_columns(columns: dict):
        """
        This function will check the contents of the dictionary and ensure that at least the latitude, longitude, and
        altitude columns are listed within the object.
        :param columns:
            A dictionary containing the names of the columns as data, and the required names of the fields are keys
        :raises ValueError:
            A ValueError is raised if there are required fields that are missing from the dictionary
        :return:
            True if all required fields are present, ValueError otherwise
        """

        if "latitude" not in columns.keys():
            raise ValueError("You must provide a latitude location for the creation of the flight track")
        if "longitude" not in columns.keys():
            raise ValueError("You must provide a longitude location for the creation of the flight track")
        if not (("altitude_ft_agl" in columns.keys()) or
                ("altitude_m_agl" in columns.keys()) or
                ("altitude_ft_msl" in columns.keys()) or
                ("altitude_m_msl" in columns.keys())):
            raise ValueError("You must provide a altitude for the creation of the flight track")
        if not (("heading_deg" in columns.keys()) or ("heading_rad" in columns.keys())):
            raise ValueError("You must provide a heading for the determination of the orientation of the vehicle")
        if not (("pitch_deg" in columns.keys()) or ("pitch_rad" in columns.keys())):
            raise ValueError("You must provide a pitch for the determination of the orientation of the vehicle")
        if not (("roll_deg" in columns.keys()) or ("roll_rad" in columns.keys())):
            raise ValueError("You must provide a roll for the determination of the orientation of the vehicle")
        if not (("time" in columns.keys()) or ("tpm" in columns.keys())):
            raise ValueError("You must provide a measurement time for the vehicle")

        return True

    @property
    def length(self):
        return len(self.points)

    @property
    def points(self):
        return self._points

    @property
    def __geo_interface__(self):
        positions = []
        for pt in self.points:
            positions.append(geojson.dumps(pt))
        return positions

    def distance_to(self, x: CartesianCoordinate):
        """
        This function returns an array of lengths that represents the distance from each SourcePoint object to the
        reference location defined by 'x'.
        :param x:
            The reference location that each source point is compared with
        :return:
            ndarray of Length objects representing the straight line distance from each source point to the reference
            point
        """
        distance = np.empty(self.points.shape, dtype=Length)

        for i in range(self.length):
            distance[i] = self.points[i].distance_to(x)

        return distance

    def save(self, filename: str):
        """
        This will write the contents of the track to a geojson compatible file. The contents will be stored as a
        sequence of Points to enable the storage of the additional properties of the SourcePoint
        :param filename:
            The location of the file that will hold the information from the points
        """
        from geojson import Feature, FeatureCollection, Point

        #   1. Create a list of features
        features = list()

        for i in range(self.length):
            pt = self.points[i]

            features.append(
                Feature(
                    geometry=Point(coordinates=list(pt.array)),
                    properties={'heading': pt.heading_degrees,
                                'pitch': pt.pitch_degrees,
                                'roll': pt.roll_degrees}
                    )
                )

        #   2. Create the feature collection
        collection = FeatureCollection(features)

        #   3. Dump this to a file
        with open(filename, 'a') as file:
            geojson.dump(collection, file)

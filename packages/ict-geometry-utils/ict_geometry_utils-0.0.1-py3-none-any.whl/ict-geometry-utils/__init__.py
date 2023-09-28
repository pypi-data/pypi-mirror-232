import math
import numpy as np


class GeometryUtils:
    @staticmethod
    def extract_point(point):
        if point is None:
            return None

        return point[0], point[1]

    @staticmethod
    def line_between_points(point1, point2):
        x1, y1 = GeometryUtils.extract_point(point1)
        x2, y2 = GeometryUtils.extract_point(point2)

        if x2 - x1 == 0:
            slope = float('inf')
        else:
            slope = (y2 - y1) / (x2 - x1)

        intercept = y1 - slope * x1

        return slope, intercept

    @staticmethod
    def is_point_above_line(point, line_point1, line_point2, y_growing_up=True):
        x, y = GeometryUtils.extract_point(point)
        slope, intercept = GeometryUtils.line_between_points(line_point1, line_point2)
        if slope != float('inf'):
            y_on_line = round(slope * x + intercept)
            if y_growing_up:
                return y > y_on_line, y == y_on_line
            else:
                return y < y_on_line, y == y_on_line
        else:
            # rect_point1 and rect_point2 have the same x
            # rect equation is something like x = k
            x_on_rect = line_point1[0]
            return x > x_on_rect, x == x_on_rect

    @staticmethod
    def point_distance(point1, point2, round_digits=None):
        x1, y1 = GeometryUtils.extract_point(point1)
        x2, y2 = GeometryUtils.extract_point(point2)

        distance = math.dist([x1, y1], [x2, y2])

        return round(distance, round_digits) if round_digits is not None else distance

    @staticmethod
    def angle_between_lines(slope1, slope2, in_degrees=False):
        relative_slope = slope1 * slope2

        # Checking if they are perpendicular
        if relative_slope == -1:
            angle = math.pi / 2
        else:
            slope_angle1 = math.atan(slope1)
            slope_angle2 = math.atan(slope2)
            angle = abs(slope_angle1 - slope_angle2)

        return angle if not in_degrees else math.degrees(angle)

    @staticmethod
    def angle_between_line_and_y(slope, in_degrees=False):
        # Checking if they are perpendicular
        if slope == 0:
            angle = math.pi / 2
        else:
            slope_angle1 = math.pi / 2
            slope_angle2 = math.atan(slope)
            angle = abs(slope_angle1 - slope_angle2)

        return angle if not in_degrees else math.degrees(angle)

    @staticmethod
    def angle_between_line_and_x(slope, in_degrees=False):
        slope_angle1 = 0
        slope_angle2 = math.atan(slope)
        angle = abs(slope_angle1 - slope_angle2)

        return angle if not in_degrees else math.degrees(angle)

    @staticmethod
    def find_parabola(p1, p2, p3):
        x = np.array([p1[0], p2[0], p3[0]])
        y = np.array([p1[1], p2[1], p3[1]])

        # Grado del polinomio desiderato
        deg = 2

        # Esegui la regressione polinomiale
        return np.polyfit(x, y, deg)

import random
from itertools import combinations
from itertools import product, chain, combinations
from shapely.geometry import LineString, Point, Polygon
import math
class MACHINE():
    """
        [ MACHINE ]
        MinMax Algorithm을 통해 수를 선택하는 객체.
        - 모든 Machine Turn마다 변수들이 업데이트 됨

        ** To Do **
        MinMax Algorithm을 이용하여 최적의 수를 찾는 알고리즘 생성
           - class 내에 함수를 추가할 수 있음
           - 최종 결과는 find_best_selection을 통해 Line 형태로 도출
               * Line: [(x1, y1), (x2, y2)] -> MACHINE class에서는 x값이 작은 점이 항상 왼쪽에 위치할 필요는 없음 (System이 organize 함)
    """
    def __init__(self, score=[0, 0], drawn_lines=[], whole_lines=[], whole_points=[], location=[]):
        self.id = "MACHINE"
        self.score = [0, 0] # USER, MACHINE
        self.drawn_lines = [] # Drawn Lines
        self.board_size = 7 # 7 x 7 Matrix
        self.num_dots = 0
        self.whole_points = []
        self.location = []
        self.triangles = [] # [(a, b), (c, d), (e, f)]

    def find_best_selection(self):
        # 가능한 선분들
        available = [[point1, point2] for (point1, point2) in list(combinations(self.whole_points, 2)) if self.check_availability([point1, point2])]
        max_distance = 0 # 가장 멀리 그을 수 있는거 (단독/연결 고려 X)
        max_index = 0  # 이때의 index
        max_disconnected_index = -1  # 아무것도 연결 안되어있는것중에 긴 선분의 index

        getPoint = []

        # 삼각형 만들 수 있으면 바로 만들기
        for i in range(len(available)):
            line = available[i]
            
        # 1. 삼각형 만들 수 있으면 바로 ㄱ
            #삼각형 2개 만들수있을때
            if(self.check_triangle(line)==2):
                return line
            #삼각형 1개
            if(self.check_triangle(line)==1):
                getPoint.append(line)
        # 2. 가장 길게 그을 수 있는거
            distance = math.sqrt((line[0][0]-line[1][0])**2 + (line[0][1]-line[1][1])**2)
            if(max_distance<distance):
                #안겹치는 것 중 제일 긴 선분 (임시로 한것)
                checkLine = True
                for j in self.drawn_lines:
                    if j[0]==line[0] or j[0]==line[1] or j[1]==line[0] or j[1]==line[1]:
                        checkLine = False
                        break
                if checkLine:    
                    max_distance = distance
                    max_index = i
            
        # 만들 수 있는 삼각형 없으면 다른 선분과 안겹치게 긋기 (임시로 한것)
        if getPoint:
            return random.choice(getPoint)
        else:
            return available[max_index]

        #return random.choice(available)
    
    def check_triangle(self, line):
        score = 0

        point1 = line[0]
        point2 = line[1]

        point1_connected = []
        point2_connected = []

        for l in self.drawn_lines:
            if l==line: # 자기 자신 제외
                continue
            if point1 in l:
                point1_connected.append(l)
            if point2 in l:
                point2_connected.append(l)

        if point1_connected and point2_connected: # 최소한 2점 모두 다른 선분과 연결되어 있어야 함
            # product는 모든 조합 구해줌
            for line1, line2 in product(point1_connected, point2_connected):
                if(line1[0] in line2 or line1[1] in line2):
                    tripoint1 = line1[0]
                    tripoint2 = line1[1]
                    if(line2[0] == tripoint1 or line2[0] == tripoint2):
                        tripoint3 = line2[1]
                    else:
                        tripoint3 = line2[0]
                    if self.check_pointIntri(tripoint1, tripoint2, tripoint3):
                        continue
                    print("3개의 선: ", line, line1, line2)
                    score += 1
        return score
        
    #삼각형 내부의 점 체크
    def check_pointIntri(self, tripoint1, tripoint2, tripoint3):
        triangle = Polygon([tripoint1, tripoint2, tripoint3])
        for point in self.whole_points:
            p = Point(point)
            if(p == tripoint1 or p == tripoint2 or p == tripoint3):
                continue
            else:
                if p.within(triangle):
                    return True
        return False
    
    def check_availability(self, line):
        line_string = LineString(line)

        # Must be one of the whole points
        condition1 = (line[0] in self.whole_points) and (line[1] in self.whole_points)
        
        # Must not skip a dot
        condition2 = True
        for point in self.whole_points:
            if point==line[0] or point==line[1]:
                continue
            else:
                if bool(line_string.intersection(Point(point))):
                    condition2 = False

        # Must not cross another line
        condition3 = True
        for l in self.drawn_lines:
            if len(list(set([line[0], line[1], l[0], l[1]]))) == 3:
                continue
            elif bool(line_string.intersection(LineString(l))):
                condition3 = False

        # Must be a new line
        condition4 = (line not in self.drawn_lines)

        if condition1 and condition2 and condition3 and condition4:
            return True
        else:
            return False    
            

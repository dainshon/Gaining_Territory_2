import random
from shapely.geometry import LineString, Point
from itertools import combinations
from shapely.geometry import LineString, Point


# min max 화요일 11시까지 구현하기
# heuristic은 그냥 돌아가는 구현 정도만 !
# 브랜치 파서 푸쉬 후에 비교

class MACHINE():
    def __init__(self, score=[0, 0], drawn_lines=[], whole_lines=[], whole_points=[], location=[]):
        self.id = "MACHINE"
        self.score = [0, 0] # USER, MACHINE
        self.drawn_lines = [] # Drawn Lines
        self.board_size = 7 # 7 x 7 Matrix
        self.num_dots = 0
        self.whole_points = []
        self.location = []
        self.triangles = [] # [(a, b), (c, d), (e, f)]

    def minmax(self, depth, is_maximizing):
        # 깊이 0이면
        # if depth == 0 or self.is_end():
        #     return self.go_heuristic()


        # min max + alpha beta prunning 적용
        # 짜보니까 알고리즘은 다 같음 여기서 내는 아이디어가 중요할듯
        # + ) 아이디어 : 대각선으로 크게 긋기 + 한 번 접근한 점은 가중치 ? 추가 점수 부여하는게 어떤지
        # 승리에 기여하는 조건 찾고 그거에 가중치 주는방식 어떤가 ...
        if is_maximizing:
            # - 무한대
            max_eval = float('-inf')
            lines = self.get_available_lines()
            for line in lines:
                self.drawn_lines.append(line)
                eval = self.minmax(depth - 1, False)
                self.drawn_lines.remove(line)
                max_eval = max(max_eval, eval)
            return max_eval
        else:
            # + 무한대
            min_eval = float('inf')
            lines = self.get_available_lines()
            for line in lines:
                self.drawn_lines.append(line)
                eval = self.minmax(depth - 1, True)
                self.drawn_lines.remove(line)
                min_eval = min(min_eval, eval)
            return min_eval

    def find_best_selection(self):
        max_eval = float('-inf')
        best_line = None
        for line in self.get_available_lines():
            self.drawn_lines.append(line)
            eval = self.minmax(3, False)  # 일단 3
            self.drawn_lines.remove(line)
            if eval > max_eval:
                max_eval = eval
                best_line = line
        return best_line

    def get_available_lines(self):
        all_lines = list(combinations(self.whole_points, 2))
        available_lines = []
        for line in all_lines:
            if self.check_availability(line) and line not in self.drawn_lines:
                available_lines.append(line)
        return available_lines


    def check_availability(self, line):
        line_string = LineString(line)

        # Must be one of the whole points
        condition1 = (line[0] in self.whole_points) and (line[1] in self.whole_points)

        # Must not skip a dot
        condition2 = True
        for point in self.whole_points:
            if point == line[0] or point == line[1]:
                continue
            else:
                if bool(line_string.intersection(Point(point))):
                    condition2 = False

        # Must not cross another line
        condition3 = True
        for l in self.drawn_lines:
            if len(list({line[0], line[1], l[0], l[1]})) == 3:
                continue
            elif bool(line_string.intersection(LineString(l))):
                condition3 = False

        # Must be a new line
        condition4 = (line not in self.drawn_lines)

        if condition1 and condition2 and condition3 and condition4:
            return True
        else:
            return False


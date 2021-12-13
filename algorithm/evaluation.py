from types import GetSetDescriptorType
from pygame.constants import BLENDMODE_ADD
from game.grid import Grid

class Evaluation:   
    GAME_OVER           = -9999999999
    INFINITY            = 999999999999 

    # WEIGHTS_MATRIX      = [
    #     [1 ** 1, 4 ** 1, 5 ** 1, 4 ** 2],
    #     [4 ** 4, 5 ** 3, 4 ** 3, 5 ** 2],
    #     [4 ** 5, 5 ** 5, 4 ** 6, 5 ** 6],
    #     [3** 11, 5 ** 7, 4 ** 8, 4 ** 7]
    # ]

    WEIGHTS_MATRIX       = [
        [
            [10, 7, 3, 1],
            [100, 70, 30, 10],
            [1000, 700, 300, 100],
            [40000, 7000, 3000, 1000],
        ],
        [
            [1, 3, 7, 10],
            [10, 30, 70, 100],
            [200, 600, 1400, 2000],
            [40000, 7000, 3000, 2000],
        ],
        [
            [10, 7, 3, 1],
            [200, 140, 60, 20],
            [200, 600, 1400, 2000],
            [40000, 7000, 3000, 2000],
        ],
        [
            [2, 6, 14, 20],
            [200, 140, 60, 20],
            [200, 600, 1400, 2000],
            [40000, 7000, 3000, 2000],
        ]
    ]
                          
    def __init__(self) -> None:
        self.ROW            = 4
        self.COLUMN         = 4

    def evaluate(self, grid: Grid, is_movement: bool) -> int:
        """
        Evaluate the score of the board

        Parameters
        ----------
        grid: Grid

        is_movement: bool

        Returns
        -------
            evaluation: int
                return the evaluation value
        """
        if grid.has_no_move():
            return self.GAME_OVER
        
        total = 0
        total += 2 * self.__evaluate_tiles_order(grid, is_movement)
        total += 1 * self.__evaluate_average(grid.board)
        total += 40 * self.__evaluate_potential_merge(grid.board)
        total += 30 * self.__evaluate_empty_tile(grid.board)
        return total
        
    def __evaluate_average(self, board: list) -> int:
        s, cnt          = 0, 0
        for row in board:
            for x in row:
                s      += x
                cnt    += 1 if x > 0 else 0
        
        return s // cnt
    
    def __evaluate_empty_tile(self, board: list) -> int:
        cnt             = 0
        for row in board:
            for x in row:
                cnt    += 1 if x == 0 else 0
        
        return cnt

    def __evaluate_potential_merge(self, board: list) -> int:
        used_in_R       = [[False for c in range(self.COLUMN)] for r in range(self.ROW)]
        used_in_C       = [[False for c in range(self.COLUMN)] for r in range(self.ROW)]
        cnt             = 0

        for r in range(self.ROW):
            for c in range(self.COLUMN):

                if r + 1 < self.ROW and board[r][c] == board[r + 1][c]:
                    if used_in_R[r][c] == False and used_in_R[r + 1][c] == False:
                        cnt                    += board[r][c] * 2
                        used_in_R[r][c]         = True
                        used_in_R[r + 1][c]     = True    
                    
                if c + 1 < self.COLUMN and board[r][c] == board[r][c + 1]:
                    if used_in_C[r][c] == False and used_in_C[r][c + 1] == False:
                        cnt                    += board[r][c] * 2
                        used_in_C[r][c]         = True
                        used_in_C[r][c + 1]     = True

        return cnt

    def __choose_weight_index(self, board: list, is_strict: bool) -> int:
        """
        + Choose the suitable weight matrix for the evaluation
        + This bases on the playing strategy of the AI
            - It check from the last row to the first one
            - If the last row is not good, use 0
            - If the last row is good enough, use 1
            - If the last row and the second last row is good enough, use 2
            - And so on ...
        """
        # store to a new array
        values = list()
        for row in board:
            for x in row:
                values.append(x)

        values.sort(reverse=True)    

        def is_good_enough(r, reverse) -> bool:    
            if reverse:
                index_c = range(self.COLUMN - 1, -1, -1)
            else:
                index_c = range(self.COLUMN)

            strike = 0
            
            for c in index_c:
                if values[0] != 0:
                    if values[0] == board[r][c]:
                        values.pop(0)
                        strike += 1
                    elif is_strict is False and strike == 3 and values[1] != 0 and values[1] == board[r][c]:
                        values.pop(1)
                    else:
                        return False
                else:
                    return False

            return True

        idx = 0
        for r in range(self.ROW - 1, 0, -1):
            if is_good_enough(r, not bool(r % 2)):
                idx += 1
            else:
                break

        return idx
    
    def __evaluate_tiles_order(self, grid: Grid, is_movement: bool) -> int:
        if is_movement:
            if (
                grid.can_move_left() is False
                and grid.can_move_right() is False
                and grid.can_move_down() is False
            ):
                return self.GAME_OVER
        
        cnt = 0
        idx = self.__choose_weight_index(grid.board, False)
        # => có phần strict và non-strict, cả hai đều có kết quả tốt
        # để non-strict chữa lỗi tốt hơn
        # còn để strict nếu ko có lỗi khi chơi sẽ cho kết quả tốt hơn
        # idx = 3
        
        for r in range(self.ROW):
            for c in range(self.COLUMN):
                cnt += grid.board[r][c] * self.WEIGHTS_MATRIX[idx][r][c]

        return cnt
    
    # WEIGHTS_MATRIX       = [
    #     [
    #         [100, 75, 50, 25],
    #         [500, 400, 300, 200],
    #         [1000, 850, 750, 600],
    #         [5000, 1500, 1200, 1100],
    #     ],
    #     [
    #         [25, 50, 75, 100],
    #         [200, 300, 400, 500],
    #         [600, 750, 850, 1000],
    #         [5000, 1500, 1200, 1100]
    #     ],
    #     [
    #         [100, 75, 50, 25],
    #         [500, 400, 300, 200],
    #         [600, 750, 850, 1000],
    #         [5000, 1500, 1200, 1100]
    #     ],
    #     [
    #         [25, 50, 75, 100],
    #         [500, 400, 300, 200],
    #         [600, 750, 850, 1000],
    #         [5000, 1500, 1200, 1100]
    #     ]
    # ]

    # WEIGHTS_MATRIX       = [
    #     [
    #         [10, 8, 5, 2],
    #         [100, 85, 50, 25],
    #         [1000, 850, 500, 250],
    #         [10000, 8500, 5000, 2500],
    #     ],
    #     [
    #         [2, 5, 8, 10],
    #         [25, 50, 85, 100],
    #         [1000, 850, 500, 250],
    #         [10000, 8500, 5000, 2500],
    #     ],
    #     [
    #         [10, 8, 5, 2],
    #         [100, 85, 50, 25],
    #         [200, 500, 850, 1000],
    #         [10000, 8500, 5000, 2500],
    #     ],
    #     [
    #         [2, 5, 8, 10],
    #         [100, 85, 50, 25],
    #         [200, 500, 850, 1000],
    #         [10000, 8500, 5000, 2500],
    #     ]
    # ]

    # WEIGHTS_MATRIX       = [
    #     [
    #         [10, 7, 4, 1],
    #         [100, 70, 40, 10],
    #         [1000, 700, 400, 100],
    #         [10000, 7000, 4000, 1000],
    #     ],
    #     [
    #         [1, 4, 7, 10],
    #         [10, 40, 70, 100],
    #         [200, 400, 700, 1000],
    #         [10000, 7000, 4000, 1000],
    #     ],
    #     [
    #         [10, 7, 4, 1],
    #         [100, 70, 40, 10],
    #         [200, 400, 700, 1000],
    #         [10000, 7000, 4000, 1000],
    #     ],
    #     [
    #         [1, 4, 7, 10],
    #         [100, 70, 40, 10],
    #         [200, 400, 700, 1000],
    #         [10000, 7000, 4000, 1000],
    #     ]
    # ]

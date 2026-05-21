import polars as pl
import numpy as np
from plotnine import (
    ggplot,
    aes,
    geom_rect,
    theme_minimal,
    scale_fill_manual,
    theme,
    element_blank,
)
from typing import List, Tuple
from enum import Enum
from ninejs import interactive, save


class MondrianColour(Enum):
    BLACK = "#000000"
    YELLOW = "#FDDE06"
    BLUE = "#0300AD"
    RED = "#E70503"
    WHITE = "#ffffff"


class Node:
    def __init__(
        self, depth: int, x_range: Tuple[float, float], y_range: Tuple[float, float]
    ):
        self.depth = depth
        self.x_range = x_range
        self.y_range = y_range
        self.left = None
        self.right = None
        self.split_value = None
        self.is_vertical = np.random.choice([True, False])


def generate_tree(
    node: Node, max_depth: int, min_size: float, force_split: bool = False
) -> None:
    width = node.x_range[1] - node.x_range[0]
    height = node.y_range[1] - node.y_range[0]

    if not force_split:
        if node.depth >= max_depth or (np.random.random() < 0.1 and node.depth > 1):
            return

        if width < min_size and height < min_size:
            return

    if node.is_vertical and width >= min_size:
        node.split_value = np.random.uniform(
            node.x_range[0] + min_size, node.x_range[1] - min_size
        )
        node.left = Node(
            node.depth + 1, (node.x_range[0], node.split_value), node.y_range
        )
        node.right = Node(
            node.depth + 1, (node.split_value, node.x_range[1]), node.y_range
        )
    elif not node.is_vertical and height >= min_size:
        node.split_value = np.random.uniform(
            node.y_range[0] + min_size, node.y_range[1] - min_size
        )
        node.left = Node(
            node.depth + 1, node.x_range, (node.y_range[0], node.split_value)
        )
        node.right = Node(
            node.depth + 1, node.x_range, (node.split_value, node.y_range[1])
        )
    else:
        return

    generate_tree(node.left, max_depth, min_size)
    generate_tree(node.right, max_depth, min_size)


def initial_splits(root: Node, min_size: float) -> None:
    # Vertical split
    root.is_vertical = True
    root.split_value = np.random.uniform(
        root.x_range[0] + min_size, root.x_range[1] - min_size
    )
    root.left = Node(1, (root.x_range[0], root.split_value), root.y_range)
    root.right = Node(1, (root.split_value, root.x_range[1]), root.y_range)

    # Horizontal splits
    root.left.is_vertical = False
    root.left.split_value = np.random.uniform(
        root.left.y_range[0] + min_size, root.left.y_range[1] - min_size
    )
    root.left.left = Node(
        2, root.left.x_range, (root.left.y_range[0], root.left.split_value)
    )
    root.left.right = Node(
        2, root.left.x_range, (root.left.split_value, root.left.y_range[1])
    )

    root.right.is_vertical = False
    root.right.split_value = np.random.uniform(
        root.right.y_range[0] + min_size, root.right.y_range[1] - min_size
    )
    root.right.left = Node(
        2, root.right.x_range, (root.right.y_range[0], root.right.split_value)
    )
    root.right.right = Node(
        2, root.right.x_range, (root.right.split_value, root.right.y_range[1])
    )


def tree_to_rectangles(node: Node, rectangles: List[dict]) -> None:
    if node.left is None and node.right is None:
        rectangles.append(
            {
                "xmin": node.x_range[0],
                "xmax": node.x_range[1],
                "ymin": node.y_range[0],
                "ymax": node.y_range[1],
                "depth": node.depth,
            }
        )
    else:
        tree_to_rectangles(node.left, rectangles)
        tree_to_rectangles(node.right, rectangles)


np.random.seed(42)

root = Node(0, (0, 1), (0, 1))
min_size = 0.05
max_depth = 12

# Perform initial splits
initial_splits(root, min_size)

# Continue generating the tree
generate_tree(root.left.left, max_depth, min_size)  # pyrefly: ignore
generate_tree(root.left.right, max_depth, min_size)  # pyrefly: ignore
generate_tree(root.right.left, max_depth, min_size)  # pyrefly: ignore
generate_tree(root.right.right, max_depth, min_size)  # pyrefly: ignore

rectangles = []
tree_to_rectangles(root, rectangles)

colours = pl.Series(
    name="colour",
    values=np.random.choice(
        [colour.value for colour in MondrianColour], size=len(rectangles)
    ),
)

df = pl.DataFrame(rectangles).with_columns(colours)

plot = (
    ggplot(
        df,
        aes(
            xmin="xmin",
            xmax="xmax",
            ymin="ymin",
            ymax="ymax",
            fill="colour",
            tooltip="colour",
            data_id="colour",
        ),
    )
    + geom_rect(color="black", size=2)
    + scale_fill_manual(values=[colour.value for colour in MondrianColour])
    + theme_minimal()
    + theme(
        legend_position="none",
        aspect_ratio=1,
        axis_text=element_blank(),
        axis_ticks=element_blank(),
        panel_grid=element_blank(),
        figure_size=(10, 10),
    )
)

interactive(plot) + save("docs/iframes/mondrian.html", minify=True)

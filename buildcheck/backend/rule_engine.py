from .vectorization import *
from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Callable
from copy import deepcopy
from shapely import Point


# This MUST be kept up to date with the `guidelines` table at all times
class Guidelines(Enum):
	LAYOUT_HAS_ROOM = 1
	ROOMS_HAVE_DOOR = 2
	ROOMS_HAVE_DIM = 3
	ROOM_DIMS_APPROPRIATE = 4
	ROOM_AREA_APPROPRIATE = 5




class GuidelineCategory(Enum):
	STRUCTURAL = "structural"
	EXTERIOR = "exterior"
	ZONING = "zoning"


@dataclass(frozen=True)
class Guideline:
	gid: Guidelines
	title: str
	description: str
	category: GuidelineCategory






@dataclass
class Failure:
	guideline: Guideline
	location: Optional[Point] = None


Verdict = list[Failure]  # empty list denotes no failures
Rule = Callable[Layout, Verdict]



def validate(layout: Layout, rules: list[Rule]) -> list[Failure]:
	all_failures = []

	# run each rule on the layout
	# collect the failures then return them

	for rule in rules:
		failures = rule(layout)
		all_failures += failures

	return all_failures


#
# MARK - Rules
#




def rule_at_least_one_room(layout: Layout) -> Verdict:
	if not len(layout.rooms) > 0:
		return [Failure(Guidelines.LAYOUT_HAS_ROOM)]
	else:
		return []


def rule_every_room_door(layout: Layout) -> Verdict:

	failures = []

	def has_door(room):
		return any(sym.category == Category.DOOR for sym in room.symbols)

	for room in layout.rooms:
		if not has_door(room):
			# for the location, we just pick a random junction for now
			# later when we have shapely, we can compute the centroid of the polygon
			failures.append(Failure(Guidelines.ROOMS_HAVE_DOOR, location=room.polygon.centroid))

	return failures


def rule_every_room_has_dimension(layout: Layout) -> Verdict:

	failures = []

	def has_dim(room):
		return any(isinstance(meta, Dimension) for meta in room.metadata)

	for room in layout.rooms:
		if not has_dim(room):
			failures.append(Failure(Guidelines.ROOMS_HAVE_DIM, location=room.polygon.centroid))

	return failures


def rule_room_area_appropriate(layout: Layout) -> Verdict:

	failures = []

	MAX_AREA = 110  # we assume m so m^2

	def area_appropriate(dim: Dimension):
		return 0 < dim.width * dim.height < MAX_AREA

	for room in layout.rooms:
		# we don't worry about checking if they have dims here
		# cuz we have an extra rule
		if room.dims:
			dim = room.dims[0]
			if not area_appropriate(dim):
				failures.append(Failure(Guidelines.ROOM_AREA_APPROPRIATE, location=room.polygon.centroid))

	return failures




def rule_room_dims_appropriate(layout: Layout) -> Verdict:

	failures = []

	MIN_WIDTH, MAX_WIDTH = 2, 200
	MIN_HEIGHT, MAX_HEIGHT = 2, 200

	def dims_appropriate(dim: Dimension):
		return MIN_WIDTH < dim.width < MAX_WIDTH and MIN_HEIGHT < dim.height < MAX_HEIGHT

	for room in layout.rooms:
		# we don't worry about checking if they have dims here
		# cuz we have an extra rule
		if room.dims:
			dim = room.dims[0]
			if not dims_appropriate(dim):
				failures.append(Failure(Guidelines.ROOM_DIMS_APPROPRIATE, location=room.polygon.centroid))

	return failures



ajyal_guidelines: list[Rule] = [
	rule_at_least_one_room,
	rule_every_room_door,
	rule_every_room_has_dimension,
	rule_room_dims_appropriate,
	rule_room_area_appropriate,
]


def validate_ajyal(layout: Layout) -> list[Failure]:
	return validate(layout, ajyal_guidelines)






# origin is top left corner because we are using image coords

# TODO maybe we have to assume a real world scale to enforce rules about dimensions




if __name__ == '__main__':


	from pprint import pprint


	def makepts(pts: list[list[int]]):
		return [Point(*p) for p in pts]


	# create basic room
	room_basic_nodoor = Room(
		junctions = [
			# should be ccw order
			Point(0, 0),  # top left
			Point(0, 5),  # bot left
			Point(5, 5),  # bot right
			Point(5, 0),  # top right
		],
		symbols = []  # no door
	)

	door_within_bounds = Symbol(Category.DOOR, BBox(*makepts([[1,1], [1,2], [2,1], [2,2]])))

	# create room with door by cloning and adding a symbol
	room_basic_door = deepcopy(room_basic_nodoor)
	room_basic_door.symbols.append(door_within_bounds)


	# create layouts
	layout_empty = Layout(
		rooms=[],
		file_name="empty.png"
	)

	layout_bad = Layout(
		rooms=[room_basic_nodoor],
		file_name='bad.png'
	)


	layout_good = Layout(
		rooms=[room_basic_door],
		file_name='good.png'
	)

	val_empty = validate_ajyal(layout_empty)
	val_bad = validate_ajyal(layout_bad)
	val_good = validate_ajyal(layout_good)


	print("Validation Results")
	print("empty::")
	pprint(val_empty)

	print("bad::")
	pprint(val_bad)

	print("good::")
	pprint(val_good)




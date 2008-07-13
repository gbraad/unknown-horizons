# ###################################################
# Copyright (C) 2008 The OpenAnno Team
# team@openanno.org
# This file is part of OpenAnno.
#
# OpenAnno is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# ###################################################

from building import UnselectableBuilding
import fife
import game.main
import math

class Path(UnselectableBuilding):
	@classmethod
	def getBuildList(cls, point1, point2):
		"""
		@param point1:
		@param point2:
		"""
		island = None
		settlement = None
		buildings = []
		y = int(round(point1[1]))
		for x in xrange(int(round(point1[0])), int(round(point2[0])), (1 if int(round(point2[0])) > int(round(point1[0])) else -1)):
			new_island = game.main.session.world.get_island(x, y)
			if new_island is None or (island is not None and island != new_island):
				continue
			island = new_island

			new_settlement = island.get_settlements(x, y, x, y)
			new_settlement = None if len(new_settlement) == 0 else new_settlement.pop()
			if new_settlement is None or (settlement is not None and settlement != new_settlement): #we cant build where no settlement is or from one settlement to another
				continue
			settlement = new_settlement

			buildings.append({'x' : x, 'y' : y, 'action' : ('d' if int(round(point2[0])) < int(round(point1[0])) else 'b') if len(buildings) == 0 else 'bd'})
		x = int(round(point2[0]))
		is_first = True
		for y in xrange(int(round(point1[1])), int(round(point2[1])) + (1 if int(round(point2[1])) > int(round(point1[1])) else -1), (1 if int(round(point2[1])) > int(round(point1[1])) else -1)):
			new_island = game.main.session.world.get_island(x, y)
			if new_island is None or (island is not None and island != new_island):
				continue
			island = new_island

			new_settlement = island.get_settlements(x, y, x, y)
			new_settlement = None if len(new_settlement) == 0 else new_settlement.pop()
			if new_settlement is None or (settlement is not None and settlement != new_settlement): #we cant build where no settlement is or from one settlement to another
				continue
			settlement = new_settlement

			if len(buildings) == 0: #first tile
				if y == int(round(point2[1])): #only tile
					action = 'default'
				else:
					action = 'c' if int(round(point2[1])) > int(round(point1[1])) else 'a'
			elif y == int(round(point2[1])): #last tile
				if int(round(point1[1])) == int(round(point2[1])): #only tile in this loop
					action = 'd' if int(round(point2[0])) > int(round(point1[0])) else 'b'
				else:
					action = 'a' if int(round(point2[1])) > int(round(point1[1])) else 'c'
			elif y == int(round(point1[1])): #edge
				if int(round(point2[0])) > int(round(point1[0])):
					action = 'cd' if int(round(point2[1])) > int(round(point1[1])) else 'ad'
				else:
					action = 'bc' if int(round(point2[1])) > int(round(point1[1])) else 'ab'
			else:
				action = 'ac'
			buildings.append({'x' : x, 'y' : y, 'action' : action})
			is_first = False
		return None if len(buildings) == 0 else {'island' : island, 'settlement' : settlement, 'buildings' : buildings}

	def init(self):
		"""
		"""
		super(Path, self).init()
		island = game.main.session.world.get_island(self.x, self.y)
		for tile in [island.get_tile(self.x + 1, self.y), island.get_tile(self.x - 1, self.y), island.get_tile(self.x, self.y + 1), island.get_tile(self.x, self.y - 1)]:
			if tile is not None and isinstance(tile.object, Path):
				tile.object.recalculateOrientation()
		self.recalculateOrientation()

	def remove(self):
		super(Path, self).remove()
		island = game.main.session.world.get_island(self.x, self.y)
		for tile in [island.get_tile(self.x + 1, self.y), island.get_tile(self.x - 1, self.y), island.get_tile(self.x, self.y + 1), island.get_tile(self.x, self.y - 1)]:
			if tile is not None and isinstance(tile.object, Path):
				tile.object.recalculateOrientation()

	def recalculateOrientation(self):
		"""
		"""
		action = ''
		island = game.main.session.world.get_island(self.x, self.y)
		if isinstance(island.get_tile(self.x, self.y - 1).object, (Path, Bridge)):
			action += 'a'
		if isinstance(island.get_tile(self.x + 1, self.y).object, (Path, Bridge)):
			action += 'b'
		if isinstance(island.get_tile(self.x, self.y + 1).object, (Path, Bridge)):
			action += 'c'
		if isinstance(island.get_tile(self.x - 1, self.y).object, (Path, Bridge)):
			action += 'd'
		if action == '':
			action = 'default'
		location = fife.Location(game.main.session.view.layers[1])
		location.setLayerCoordinates(fife.ModelCoordinate(int(self.x + 1), int(self.y), 0))
		self._instance.act(action, location, True)

class Bridge(UnselectableBuilding):
	#@classmethod
	#def getInstance(cls, x, y, action=None, **trash):
	#	super(Bridge, cls).getInstance(x = x, y = y, action = 'default', **trash)

	def init(self):
		"""
		"""
		super(Bridge, self).init()
		island = game.main.session.world.get_island(self.x, self.y)
		for tile in [island.get_tile(self.x + 1, self.y), island.get_tile(self.x - 1, self.y), island.get_tile(self.x, self.y + 1), island.get_tile(self.x, self.y - 1)]:
			if tile is not None and isinstance(tile.object, Path):
				tile.object.recalculateOrientation()

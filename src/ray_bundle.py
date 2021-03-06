import numpy as N

class RayBundle:
    """Contains information about a ray bundle, using equal-length arrays, the
    length of which correspond to the number of rays in a bundle. The number is 
    determined by setting the vertices, so this should be done first when 'filling
    out' a bundle.
    
    Private attributes:
    let n be the number of rays, then for each attribute, .shape[-1] == n.
    _vertices: a 2D array whose each column is the (x,y,z) coordinate of a ray 
        vertex.
    _direct: a 2D array whose each column is the unit vector composed of the 
        direction cosines of each ray.
    _energy: 1D array with the energy carried by each ray.
    """
    def set_vertices(self,  vert):
        """Sets the starting point of each ray, as well as the number of rays."""
        self._vertices = vert
    
    def get_vertices(self):
        return self._vertices
    
    def set_directions(self,  directions):
        if directions.shape != (3,  self.get_num_rays()):
            raise ValueError("Number of directions != number of rays")
        self._direct = directions
    
    def get_directions(self):
        return self._direct
    
    def set_energy(self,  energy):
        if energy.shape != (self.get_num_rays(), ):
            raise ValueError("Number of directions != number of rays")
        self._energy = energy
    
    def get_energy(self):
        return self._energy
    
    def get_num_rays(self):
        return self._vertices.shape[1]
        
    def __add__(self,  added):
        """Merge two energy bundles. return a new bundle with the rays from the 
        two bundles appearing in the order of addition.
        """
        newbund = RayBundle()
        newbund.set_vertices(N.hstack((self.get_vertices(),  added.get_vertices())))
        newbund.set_directions(N.hstack((self.get_directions(),  added.get_directions())))
        newbund.set_energy(N.hstack((self.get_energy(),  added.get_energy())))
        return newbund

    def empty_bund(self):
        """Create an empty ray bundle"""
        empty = RayBundle()
        empty_array = N.array([[],[],[]])
        empty.set_vertices(empty_array)
        empty.set_directions(empty_array)
        empty.set_energy(N.array([]))
        return empty

# Module stuff:
from numpy import random,  linalg as LA
from numpy import c_

from spatial_geometry import general_axis_rotation

def solar_disk_bundle(num_rays,  center,  direction,  radius,  ang_range):
    """Generates a ray bundle emanating from a disk, with each surface element of 
    the disk having the same ray density. The rays all point at directions uniformly 
    distributed between a given angle range from a given direction.
    Setting of the bundle's energy is left to the caller.
    Arguments: num_rays - number of rays to generate.
        center - a column 3-array with the 3D coordinate of the disk's center
        direction - a 1D 3-array with the unit average direction vector for the
            bundle.
        radius - of the disk.
        ang_range - in radians, the maximum deviation from <direction).
    Returns: a RayBundle object with the above charachteristics set.
    """
    # Divergence from <direction>:
    phi     = random.uniform(high=2*N.pi,  size=num_rays)
    theta = random.uniform(high=ang_range,  size=num_rays)
    # A vector on the xy plane (arbitrary), around which we rotate <direction> 
    # by theta:
    perp = N.array([direction[1],  -direction[0],  0])
    if N.all(perp == 0):
        perp = N.array([1.,  0.,  0.])
    
    directions = N.empty((3, num_rays))
    for ray in xrange(num_rays):
        dir = N.dot(general_axis_rotation(perp,  theta[ray]),  direction)
        dir = N.dot(general_axis_rotation(direction,  phi[ray]),  dir)
        directions[:, ray] = dir

    # Locations:
    not_inside = N.ones(num_rays,  dtype=N.bool)
    xs = N.empty(num_rays)
    ys = N.empty(num_rays)
    while not_inside.any():
        xs[not_inside] = random.uniform(low=-radius,  high=radius,  size=len(not_inside))
        ys[not_inside] = random.uniform(low=-radius,  high=radius,  size=len(not_inside))
        not_inside = xs**2 + ys**2 > radius**2
    
    # Rotate locations to the plane defined by <direction>:
    rot = N.vstack((perp,  N.cross(direction,  perp),  direction))
    vertices_local = N.array([xs,  ys,  N.zeros(num_rays)])
    vertices_global = N.dot(rot,  vertices_local)
    
    rayb = RayBundle()
    rayb.set_vertices(vertices_global + center)
    rayb.set_directions(directions)
    return rayb

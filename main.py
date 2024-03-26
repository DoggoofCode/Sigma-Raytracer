from PIL import Image


class basic_structure:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __getitem__(self, item):
        return getattr(self, item)

    def __repr__(self):
        return f"{self.__class__.__name__}-Struct({', '.join([f'{slot}={getattr(self, slot)}' for slot in self.__slots__])})"


class hit_record(basic_structure):
    __slots__ = ["p", "normal", "t"]


class vec3:
    def __init__(self, e0: float, e1: float, e2: float) -> None:
        self.e = [e0, e1, e2]

    def __neg__(self):
        return vec3(-self.e[0], -self.e[1], -self.e[2])

    def __getitem__(self, item):
        return self.e[item]

    def __add__(self, other: "vec3"):
        return vec3(self.e[0] + other.e[0], self.e[1] + other.e[1], self.e[2] + other.e[2])

    def __sub__(self, other):
        return vec3(self.e[0] - other.e[0], self.e[1] - other.e[1], self.e[2] - other.e[2])

    def __mul__(self, other):
        return vec3(self.e[0] * other, self.e[1] * other, self.e[2] * other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        return self.__mul__(1 / other)

    def __dot__(self, other):
        return self.e[0] * other.e[0] + self.e[1] * other.e[1] + self.e[2] * other.e[2]

    def __cross__(self, other):
        return vec3(self.e[1] * other.e[2] - self.e[2] * other.e[1],
                    self.e[2] * other.e[0] - self.e[0] * other.e[2],
                    self.e[0] * other.e[1] - self.e[1] * other.e[0])

    def __unit_vector__(self):
        return self / self.length()

    def length_squared(self):
        return self.e[0] ** 2 + self.e[1] ** 2 + self.e[2] ** 2

    def length(self):
        return self.length_squared() ** 0.5

    def __repr__(self):
        return f"vec3({self.e[0]}, {self.e[1]}, {self.e[2]})"

    @property
    def x(self):
        return self.e[0]

    @property
    def y(self):
        return self.e[1]

    @property
    def z(self):
        return self.e[2]


class ray:
    def __init__(self, origin: vec3, direction: vec3):
        self.origin = origin
        self.direction = direction

    def at(self, t: float) -> vec3:
        return self.origin + t * self.direction


class point3(vec3):
    pass


class color(vec3):
    pass


class Sphere:
    def __init__(self, center: point3, radius: float):
        self.center = center
        self.radius = radius

    def hit(self, r: ray, t_min: float, t_max: float, hit_record: "hit_record") -> bool:
        oc = r.origin - self.center
        a = r.direction.length_squared()
        half_b = oc.__dot__(r.direction)
        c = oc.length_squared() - self.radius ** 2
        discriminant = half_b ** 2 - a * c
        if discriminant < 0: return False
        sqrtd = discriminant ** 0.5

        root = (-half_b - sqrtd) / a
        if root < t_min or t_max < root:
            return False

        hit_record.t = root
        hit_record.p = r.at(hit_record.t)
        hit_record.normal = (hit_record.p - self.center) / self.radius

        return True


class Sphere_List:
    def __init__(self):
        self.spheres = []

    def add(self, sphere: "Sphere"):
        self.spheres.append(sphere)

    def hit(self, r: ray, t_min: float, t_max: float, hit_r: "hit_record") -> bool:
        hit_anything = False
        closest_so_far = t_max

        for sphere in self.spheres:
            if sphere.hit(r, t_min, closest_so_far, hit_r):
                hit_anything = True
                closest_so_far = hit_r.t

        return hit_anything


def write_color(pixel_color: color, xy: tuple[int, int], image_object: Image) -> None:
    ir = int(255.999 * pixel_color.x)
    ig = int(255.999 * pixel_color.y)
    ib = int(255.999 * pixel_color.z)
    image_object.putpixel(xy, (ir, ig, ib))


def hitSphere(center: point3, radius: float, r: ray) -> float:
    oc = r.origin - center
    a = r.direction.length_squared()
    half_b = oc.__dot__(r.direction)
    c = oc.length_squared() - radius ** 2
    discriminant = half_b ** 2 - a * c
    if discriminant < 0:
        return -1
    else:
        return (-half_b - discriminant ** 0.5) / a


def getColour(r: ray) -> color:
    unit_direction = r.direction.__unit_vector__()
    t = 0.5 * (unit_direction.y + 1.0)
    return (1.0 - t) * color(1.0, 1.0, 1.0) + t * color(0.5, 0.7, 1.0)


def ray_color(r: ray, world: Sphere_List) -> color:
    hit_r = hit_record()
    if world.hit(r, 0, float("inf"), hit_r):
        return 0.5 * color(hit_r.normal.x + 1, hit_r.normal.y + 1, hit_r.normal.z + 1)
    else:
        return getColour(r)


def main() -> None:
    # Image
    aspect_ratio = 16 / 9
    image_width = 1920
    image_height = int(image_width / aspect_ratio)

    # World

    world = Sphere_List()
    world.add(Sphere(point3(0, 0, -1), 0.5))
    world.add(Sphere(point3(0, -100.5, -1), 100))

    # Camera

    viewport_height = 2.0
    viewport_width = aspect_ratio * viewport_height
    focal_length = 1.0

    origin = point3(0, 0, 0)
    horizontal = vec3(viewport_width, 0, 0)
    vertical = vec3(0, viewport_height, 0)
    lower_left_corner: vec3 = origin - horizontal / 2 - vertical / 2 - vec3(0, 0, focal_length)

    # Render
    img = Image.new(mode="RGB", size=(image_width, image_height))
    for j in range(image_height - 1, -1, -1):
        if image_width > 1500:
            print(f"Scanline remaining: {j}")
        for i in range(image_width):
            u = i / (image_width - 1)
            v = j / (image_height - 1)
            r: ray = ray(origin, lower_left_corner + u * horizontal + v * vertical)  # vec

            col = ray_color(r, world)
            write_color(col, (i, j), img)

    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img.show("Image")
    save = input("Save image? [y/n]: ")
    if save == "y":
        name = input("Enter image name: ")
        img.save(f"images\\{name}.png")
        print(f"Image saved as {name}.png")


if __name__ == '__main__':
    main()

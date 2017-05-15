from math import floor, ceil

class Page(object):

    def __init__(self, number, active=False, divider=False):
        self.active = active
        self.divider = divider
        self.number = number

    def __str__(self):
        if not self.divider:
            return str(self.number)
        else:
            return "..."

class Pagination(object):

    def __init__(self, page, per_page, total_count, num_elements):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count
        self.num_elements = num_elements

        self.elements = []

        lowest = 1
        highest = self.page_count

        first = page - (num_elements//2)
        last = page + (num_elements//2)

        if first < 1 and first != 0:
            last += -(first - 1)
            first = 1
        elif first == 0:
            last += 1
            first = 1

        if last > self.page_count:
            offset = last - self.page_count
            first = max(first - offset, 1)
            last = self.page_count

        for i in range(first, last+1):
            self.elements.append(Page(i))


    @property
    def page_count(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    def get_prev_count(self):
        return self.page - 1

    def get_next_count(self):
        return self.page_count - self.page

    @property
    def has_next(self):
        return self.page < self.page_count

    def __getitem__(self, i):
        return self.elements[i]

if __name__ == "__main__":
    print("For page 1:")
    p = Pagination(1, 10, 100, 7)
    print([str(x) for x in p.elements])

    print("For page 2:")
    p = Pagination(2, 10, 100, 7)
    print([str(x) for x in p.elements])

    print("For page 3:")
    p = Pagination(3, 10, 100, 7)
    print([str(x) for x in p.elements])

    print("For page 5:")
    p = Pagination(5, 10, 200, 7)
    print([str(x) for x in p.elements])

    print("For page 16:")
    p = Pagination(16, 10, 200, 7)
    print([str(x) for x in p.elements])

    print("For page 17:")
    p = Pagination(17, 10, 200, 7)
    print([str(x) for x in p.elements])

    print("For page 20:")
    p = Pagination(20, 10, 200, 7)
    print([str(x) for x in p.elements])

import { Dropdown, DropdownTrigger, Button, DropdownMenu, DropdownItem, Table, TableHeader, TableColumn, TableBody, TableRow, TableCell } from "@heroui/react";
import { Season } from "~/data/types";

type PropType = {
  season: Season;
}

const PlayerSeasonDropdown = ({ season }: PropType) => {
  return (
    <Dropdown>
      <DropdownTrigger>
        <Button variant="flat" size="sm">
          View Stats
        </Button>
      </DropdownTrigger>
      <DropdownMenu aria-label="Season Stats" className="p-2">
        <DropdownItem key="season-stats" isReadOnly>
          <Table aria-label="Season Stats Table">
            <TableHeader>
              <TableColumn>PA</TableColumn>
              <TableColumn>R</TableColumn>
              <TableColumn>H</TableColumn>
              <TableColumn>S</TableColumn>
              <TableColumn>D</TableColumn>
              <TableColumn>T</TableColumn>
              <TableColumn>HR</TableColumn>
              <TableColumn>W</TableColumn>
              <TableColumn>HBP</TableColumn>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell>{season.plateAppearances}</TableCell>
                <TableCell>{season.runs}</TableCell>
                <TableCell>{season.hits}</TableCell>
                <TableCell>{season.singles}</TableCell>
                <TableCell>{season.doubles}</TableCell>
                <TableCell>{season.triples}</TableCell>
                <TableCell>{season.homeruns}</TableCell>
                <TableCell>{season.walks}</TableCell>
                <TableCell>{season.hitByPitch}</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </DropdownItem>
      </DropdownMenu>
    </Dropdown>
  )

}

export default PlayerSeasonDropdown;
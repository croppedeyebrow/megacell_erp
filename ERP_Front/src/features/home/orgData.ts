export type OrgMember = {
  name: string
  role: string
  /** short badge shown next to the member, e.g. '겸임', '휴직중' */
  tag?: string
  phone?: string
  extension?: string
  email?: string
}

export type OrgTeamNode = {
  slug: string
  title: string
  members: OrgMember[]
  /** sub-teams this node oversees, rendered nested below it */
  children?: OrgTeamNode[]
}

export const ORG_ROOT: OrgTeamNode = {
  slug: 'ceo',
  title: '대표이사',
  members: [
    {
      name: '이영호',
      role: '대표이사',
      phone: '010-3203-6173',
      extension: '100',
      email: 'yh6134@megacell.or.kr',
    },
  ],
  children: [
    {
      slug: 'jang-vp',
      title: '장재진 부사장',
      members: [
        {
          name: '장재진',
          role: '부사장',
          phone: '010-2776-5151',
          extension: '118',
          email: 'okjjj@megacell.or.kr',
        },
      ],
    },
    {
      slug: 'management-support',
      title: '경영지원팀',
      members: [
        {
          name: '최영균',
          role: '상무',
          phone: '010-5291-0463',
          extension: '102',
          email: 'chhoiyk@naver.com',
        },
        {
          name: '이봉준',
          role: '팀장',
          phone: '010-4002-9697',
          extension: '108',
          email: 'bjlee@megacell.or.kr',
        },
        {
          name: '김미진',
          role: '과장',
          phone: '010-5690-4029',
          extension: '107',
          email: 'mjkim@megacell.or.kr',
        },
        {
          name: '박지선',
          role: '과장',
          tag: '휴직중',
          phone: '010-4887-0070',
          email: 'pjs5253@naver.com',
        },
        {
          name: '이재성',
          role: '주임',
          phone: '010-9339-2978',
          extension: '117',
          email: 'jslee@megacell.or.kr',
        },
      ],
    },
    {
      slug: 'oversight',
      title: '총괄',
      members: [
        {
          name: '윤승언',
          role: '상무',
          phone: '010-8368-0207',
          extension: '114',
          email: 'suyun@megacell.or.kr',
        },
      ],
      children: [
        {
          slug: 'tech-sales',
          title: '기술영업팀',
          members: [
            {
              name: '최원희',
              role: '과장',
              tag: '겸임',
              phone: '010-5179-6189',
              extension: '111',
              email: 'whchoi@megacell.or.kr',
            },
          ],
        },
        {
          slug: 'rnd',
          title: '연구소',
          members: [
            {
              name: '권성문',
              role: '연구소장',
              phone: '010-4393-7202',
              extension: '103',
              email: 'smkwon@megacell.or.kr',
            },
            {
              name: '최은창',
              role: '수석연구원',
              phone: '010-2286-2793',
              extension: '113',
              email: 'ecchoi@megacell.or.kr',
            },
            {
              name: '최원희',
              role: '과장',
              tag: '겸임',
              phone: '010-5179-6189',
              extension: '111',
              email: 'whchoi@megacell.or.kr',
            },
          ],
        },
      ],
    },
    {
      slug: 'production',
      title: '생산팀',
      members: [
        {
          name: '유병진',
          role: '공장장',
          phone: '010-3735-1743',
          extension: '104',
          email: 'bjyoo@megacell.or.kr',
        },
        {
          name: '이지현',
          role: '대리',
          phone: '010-6557-4126',
          email: 'jhlee@megacell.or.kr',
        },
        {
          name: '강우진',
          role: '주임',
          phone: '010-9701-3102',
          email: 'wjkang@megacell.or.kr',
        },
        {
          name: '조성오',
          role: '주임',
          phone: '010-8295-8416',
          email: 'socho@megacell.or.kr',
        },
      ],
    },
    {
      slug: 'field-engineer',
      title: '필드엔지니어',
      members: [
        { name: '전병규', role: '부장', phone: '010-5058-7580' },
        { name: '이정환', role: '부장', phone: '010-5222-8038' },
        {
          name: '조성원',
          role: '부장',
          phone: '010-4935-9864',
          extension: '112',
          email: 'swcho@megacell.or.kr',
        },
        {
          name: '한국진',
          role: '부장',
          phone: '010-4427-7320',
          extension: '109',
          email: 'kjhan@megacell.or.kr',
        },
        {
          name: '이창식',
          role: '차장',
          phone: '010-2877-7709',
          extension: '110',
          email: 'cslee@megacell.or.kr',
        },
      ],
    },
  ],
}

export function findOrgNode(
  node: OrgTeamNode,
  slug: string,
): OrgTeamNode | undefined {
  if (node.slug === slug) return node
  for (const child of node.children ?? []) {
    const found = findOrgNode(child, slug)
    if (found) return found
  }
  return undefined
}
